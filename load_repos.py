import asyncio
import sys
from argparse import ArgumentParser
from pathlib import Path
from time import perf_counter

import aiofiles
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from tqdm.asyncio import tqdm_asyncio

HERE = Path(__file__).parent
SUFFIX_WHITELIST = {
    ".bat",
    ".c",
    ".caddy",
    ".cfg",
    ".cnf",
    ".code-workspace",
    ".conf",
    ".config",
    ".cpp",
    ".css",
    ".csv",
    ".default",
    ".dockerfile",
    ".env",
    ".gql",
    ".graphql",
    ".html",
    ".http",
    ".ini",
    ".ipynb",
    ".java",
    ".jinja2",
    ".js",
    ".json",
    ".jsp",
    ".jsx",
    ".key",
    ".log",
    ".mako",
    ".markdown",
    ".md",
    ".md5",
    ".mjs",
    ".net",
    ".npy",
    ".out",
    ".php",
    ".pub",
    ".pubkey",
    ".py",
    ".rb",
    ".sass",
    ".service",
    ".sh",
    ".swift",
    ".timer",
    ".toml",
    ".tpl",
    ".ts",
    ".txt",
    ".vue",
    ".xml",
    ".yaml",
    ".yml",
}
BLACKLIST = {"__pycache__", ".venv", ".env", "node_modules", ".git"}
SEM = asyncio.Semaphore(2000)


async def read_file(f: Path) -> str:
    codec = ["utf8", "iso8859", "big5"]
    for c in codec:
        try:
            async with aiofiles.open(f, "r", encoding=c) as fin:
                return await fin.read()
        except UnicodeDecodeError:
            pass


async def gen_es_doc(f: Path, repos_dir: Path) -> str:
    async with SEM:
        doc = {
            "_index": "code_search",
            "suffix": f.suffix.lower(),
            "namespace": "/".join(f.relative_to(repos_dir).parts[:2]),
            "path": "/".join(f.relative_to(repos_dir).parts[2:]),
            "repo_name": f.relative_to(repos_dir).parts[1],
            "file_name": f.name,
            "size": f.stat().st_size,
        }
        doc["raw"] = await read_file(f)
        return doc


def human_readable_time(sec: int) -> str:
    result = {
        "days": sec // 86400,
        "hours": sec // 3600 % 24,
        "minutes": sec // 60 % 60,
        "seconds": sec % 60,
    }
    time_str = ""
    for u in ["days", "hours", "minutes", "seconds"]:
        value = result[u]
        if value > 0:
            time_str += f"{value:.0f} {u} "
    return time_str


async def gen_data(repos_dir: Path):
    repos_dir = repos_dir.absolute()
    print("Scanning files ...")
    tasks = []
    for f in repos_dir.rglob("*"):
        if f.is_dir() or any(stopword in f.parts for stopword in BLACKLIST):
            continue
        suffix = f.suffix.lower()
        if suffix not in SUFFIX_WHITELIST:
            continue
        namespace = "/".join(f.relative_to(repos_dir).parts[:2])
        if namespace == f.name:
            continue
        tasks.append(gen_es_doc(f, repos_dir))

    for t in tqdm_asyncio.as_completed(tasks, desc="Generating documents"):
        yield await t


def build_parser():
    parser = ArgumentParser()
    parser.add_argument("repos_dir")
    parser.add_argument("--replace", action="store_true")
    parser.add_argument("--index-name", default="code_search")
    return parser


async def main():
    parser = build_parser()
    args = parser.parse_args()

    repos_dir = Path(args.repos_dir)
    if not repos_dir.exists():
        sys.exit(f"{repos_dir} not found.")

    mappings = {
        "properties": {
            "file_name": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
            },
            "namespace": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
            },
            "path": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
            },
            "repo_name": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
            },
            "raw": {"type": "text"},
            "size": {"type": "long"},
            "suffix": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
            },
        },
    }

    start_t = perf_counter()
    async with AsyncElasticsearch("http://localhost:9200", request_timeout=300) as es:
        index_name = args.index_name
        indices = await es.indices.get_alias(index="*")
        if index_name in indices.keys():
            print(f"index {index_name} is already exists.")
            if args.replace:
                await es.indices.delete(index=index_name)
                await es.indices.create(index=index_name, mappings=mappings)
                print(f"index {index_name} recreated.")
        else:
            await es.indices.create(index=index_name, mappings=mappings)
        await async_bulk(es, gen_data(Path(args.repos_dir)), chunk_size=2000)

    print(human_readable_time(perf_counter() - start_t))


if __name__ == "__main__":
    asyncio.run(main())
