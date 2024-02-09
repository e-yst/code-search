<template>
  <q-card bordered flat>
    <q-card-section class="q-gutter-md items-center justify-start">
      <div class="row items-center">
        <div class="text-h6 text-bold">{{ file.file_name }}</div>
        <q-space />
        <q-btn
          v-if="truncate"
          class="q-ml-md"
          dense
          icon="sym_o_open_in_new"
          outline
          round
          text-color="primary"
          @click="emit('show-dialog', file)"
        />
      </div>
      <div class="row">
        <div class="text-bold">{{ file.namespace }}</div>
        <div class="q-mx-sm">/</div>
        <div>{{ file.path }}</div>
      </div>
    </q-card-section>

    <q-card-section class="justify-center">
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

const emit = defineEmits<{
  'show-dialog': [file: File];
}>();

const H = ref(null);
</script>

<style lang="scss">
pre code {
  white-space: pre-wrap;
  max-width: 100%;
  overflow: scroll;
}
</style>
