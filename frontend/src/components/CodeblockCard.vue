<template>
  <q-card bordered flat>
    <q-card-section class="row q-gutter-md items-center justify-start">
      <div class="text-h6 text-bold">{{ file.file_name }}</div>
      <div>{{ file.namespace }}</div>
      <div>{{ file.path }}</div>
    </q-card-section>

    <q-card-section class="row justify-center">
      <HighCode
        ref="H"
        :code-value="
          truncate && file.raw.length > 1000
            ? file.raw.substring(0, 1000) + '...'
            : file.raw
        "
        font-size="16px"
        :height="height"
        :lang="
          file.suffix.includes('.') ? file.suffix.substring(1) : file.suffix
        "
        :max-height="maxHeight"
        :max-width="maxWidth"
        :name-show="false"
        :text-editor="true"
        :width="width"
      />
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import 'vue-highlight-code/dist/style.css';
import { File } from './models';
import { HighCode } from 'vue-highlight-code';
import { ref } from 'vue';

interface Props {
  file: File;
  truncate?: boolean;
  height?: string | undefined;
  maxHeight?: string | undefined;
  width?: string | undefined;
  maxWidth?: string | undefined;
}

withDefaults(defineProps<Props>(), {
  truncate: false,
  height: undefined,
  maxHeight: undefined,
  width: '70rem',
  maxWidth: undefined,
});
const H = ref(null);
</script>
