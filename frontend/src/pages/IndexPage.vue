<template>
  <q-page class="q-pa-xl justify-center">
    <div class="row justify-center">
      <q-form class="col" style="max-width: 50rem">
        <div class="row">
          <q-input
            v-model="searchTxt"
            class="col"
            :label="$t('search.searchbar_label')"
            outlined
            :placeholder="$t('search.searchbar_placeholder')"
            rounded
            @keyup.enter="submitQuery"
          >
            <template #append>
              <q-btn flat icon="sym_o_search" round @click="submitQuery" />
            </template>
          </q-input>
        </div>

        <div class="row justify-center">
          <q-select
            v-model="selectFileExt"
            class="col q-pt-md"
            dense
            :label="$t('search.file_extensions')"
            multiple
            :options="fileExtsOpts"
            options-dense
            outlined
            rounded
            style="max-width: 25rem"
            use-chips
            use-input
            @filter="filterFn"
          >
            <template #append>
              <q-btn
                v-show="selectFileExt.length > 0"
                dense
                flat
                icon="cancel"
                round
                @click="resetFileExts"
              />
            </template>
          </q-select>
        </div>
      </q-form>
    </div>

    <div class="q-ma-md">
      <div
        v-for="file in searchResults"
        :key="file.id"
        class="q-ma-md row justify-center"
      >
        <q-card class="" style="margin: auto; min-width: 60%">
          <q-card-section class="row q-gutter-md items-center justify-start">
            <div class="text-h6 text-bold">{{ file.file_name }}</div>
            <div>{{ file.namespace }}</div>
            <div>{{ file.path }}</div>
          </q-card-section>

          <q-card-section class="row justify-center">
            <!-- <ssh-pre
              :language="getLang(file.suffix)"
              style="
                min-width: 80rem;
                max-width: 80rem;
                max-height: 60rem;
                width: 50%;
                overflow: scroll;
              "
            >
              {{ file.raw.substring(0, 5000) }}
            </ssh-pre> -->
            <HighCode
              ref="H"
              :code-value="file.raw"
              font-size="16px"
              :height="codeblockHeight"
              :lang="
                file.suffix.includes('.')
                  ? file.suffix.substring(1)
                  : file.suffix
              "
              :name-show="false"
              :text-editor="true"
              :width="codeblockWidth"
            />
          </q-card-section>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { nextTick, onMounted } from 'vue';
import { ref } from 'vue';

import 'vue-highlight-code/dist/style.css';
import { HighCode } from 'vue-highlight-code';

const searchTxt = ref('');
const selectFileExt = ref([]);

const fileExts = ref([]);
const fileExtsOpts = ref([]);

const searchResults = ref([]);
const codeblockHeight = ref('60rem');
const codeblockWidth = ref('60rem');
const H = ref(null);

const filterFn = (val, update) => {
  update(() => {
    const needle = val.toLowerCase();
    fileExtsOpts.value = fileExts.value.filter(
      (v: string) => v.toLowerCase().indexOf(needle) > -1
    );
  });
};

const resetFileExts = () => {
  selectFileExt.value = [];
};

const queryEs = async (queryBody) => {
  const res = await fetch('/code_search/_search', {
    method: 'POST',
    cache: 'no-cache',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(queryBody),
  });
  const data = await res.json();
  return data;
};
const submitQuery = async () => {
  let queryBody = {
    query: {
      bool: {
        should: [
          { match_phrase: { raw: searchTxt.value } },
          { match_phrase: { file_name: searchTxt.value } },
        ],
      },
    },
    size: 10,
  };
  if (selectFileExt.value.length > 0)
    queryBody.query.bool.must = {
      terms: { 'suffix.keyword': selectFileExt.value },
    };
  const data = await queryEs(queryBody);
  searchResults.value = [];
  await nextTick();
  searchResults.value = data.hits.hits.map((hit) => hit._source);
  await nextTick();
};

onMounted(async () => {
  const data = await queryEs({
    size: 0,
    aggs: { uniqueExt: { terms: { field: 'suffix.keyword', size: 500 } } },
  });
  fileExts.value = data.aggregations.uniqueExt.buckets
    .map((bucket: { key: string; doc_count: number }) => bucket.key)
    .sort();
});
</script>
