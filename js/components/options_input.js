import { emitEvent } from '../lib/emitters'

export default {
  name: 'optionsinput',

  props: {
    name: String,
    initialErrors: {
      type: Array,
      default: () => [],
    },
    initialValue: String,
    watch: {
      type: Boolean,
      default: false,
    },
    optional: Boolean,
    nullOption: {
      type: String,
      default: '',
    },
  },

  created: function() {
    emitEvent('field-mount', this, {
      optional: this.optional,
      name: this.name,
      valid: this._isValid(this.value),
    })
  },

  data: function() {
    const showError = (this.initialErrors && this.initialErrors.length) || false
    return {
      showError: showError,
      showValid: false,
      validationError: this.initialErrors.join(' '),
      value: this.initialValue,
    }
  },

  methods: {
    onInput: function(e) {
      this.showError = false
      this.showValid = true
      this.value = e.target.value

      emitEvent('field-change', this, {
        value: e.target.value,
        name: this.name,
        watch: this.watch,
        valid: this._isValid(e.target.value),
      })
    },

    _isValid: function(value) {
      return this.optional || value !== this.nullOption
    },
  },
}
