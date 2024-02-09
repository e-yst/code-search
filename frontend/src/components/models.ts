export interface Todo {
  id: number;
  content: string;
}

export interface Meta {
  totalCount: number;
}

export interface File {
  file_name: string;
  namespace: string;
  path: string;
  raw: string;
  suffix: string;
}
