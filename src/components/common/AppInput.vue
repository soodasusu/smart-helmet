<template>
  <div class="app-input" :class="{ 'app-input--focused': isFocused }">
    <label v-if="label" class="app-input__label">{{ label }}</label>
    <div class="app-input__wrapper">
      <slot name="prefix" />
      <input
        :type="inputType"
        :value="modelValue"
        :placeholder="placeholder"
        :required="required"
        :disabled="disabled"
        :autocomplete="autocomplete"
        class="app-input__field"
        @input="$emit('update:modelValue', $event.target.value)"
        @focus="isFocused = true"
        @blur="isFocused = false"
        @keyup="checkCapsLock"
      />
      <button
        v-if="type === 'password'"
        type="button"
        class="app-input__toggle"
        @click="showPassword = !showPassword"
        tabindex="-1"
      >
        <svg v-if="!showPassword" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" width="18" height="18">
          <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/>
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" width="18" height="18">
          <path d="M9.88 9.88a3 3 0 1 0 4.24 4.24"/><path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c6.5 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68"/><path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3.5 7 10 7a9.74 9.74 0 0 0 5.39-1.61"/><line x1="2" y1="2" x2="22" y2="22"/>
        </svg>
      </button>
    </div>
    <span v-if="capsLockOn && type === 'password'" class="app-input__caps-warning">
      大写锁定已开启
    </span>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  modelValue: { type: String, default: '' },
  label: { type: String, default: '' },
  type: { type: String, default: 'text' },
  placeholder: { type: String, default: '' },
  required: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
  autocomplete: { type: String, default: 'off' }
})

defineEmits(['update:modelValue'])

const showPassword = ref(false)
const isFocused = ref(false)
const capsLockOn = ref(false)

const inputType = computed(() => {
  if (props.type === 'password' && showPassword.value) return 'text'
  return props.type
})

const checkCapsLock = (e) => {
  capsLockOn.value = e.getModifierState?.('CapsLock') || false
}
</script>

<style scoped>
.app-input {
  margin-bottom: var(--space-lg);
}

.app-input__label {
  display: block;
  margin-bottom: 6px;
  color: var(--color-text);
  font-weight: var(--font-weight-medium);
  font-size: var(--font-size-base);
}

.app-input__wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.app-input__field {
  width: 100%;
  padding: 11px 14px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  font-size: var(--font-size-base);
  background: var(--color-bg-input);
  color: var(--color-text);
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
  font-family: var(--font-family);
}

.app-input__field::placeholder {
  color: var(--color-text-tertiary);
}

.app-input__field:focus {
  outline: none;
  border-color: var(--color-primary-400);
  box-shadow: 0 0 0 3px var(--color-primary-100);
}

.app-input__field:disabled {
  background: var(--color-bg-subtle);
  color: var(--color-text-tertiary);
  cursor: not-allowed;
}

.app-input__toggle {
  position: absolute;
  right: 12px;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--color-text-tertiary);
  display: flex;
  align-items: center;
  transition: color var(--transition-fast);
}

.app-input__toggle:hover {
  color: var(--color-text-secondary);
}

.app-input__caps-warning {
  display: block;
  margin-top: 6px;
  font-size: var(--font-size-xs);
  color: var(--color-warning);
}
</style>
