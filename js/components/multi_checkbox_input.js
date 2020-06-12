import { emitFieldChange } from '../lib/emitters'

export default {
  name: 'multicheckboxinput',

  props: {
    name: String,
    initialErrors: {
      type: Array,
      default: () => [],
    },
    initialValue: {
      type: Array,
      default: () => [],
    },
    optional: Boolean,
  },

  data: function () {
    return {
      showError: this.initialErrors.length > 0,
      showValid: false,
      validationError: this.initialErrors.join(' '),
      selections: this.initialValue,
    }
  },

  methods: {
    onInput: function (e) {
      emitFieldChange(this)
      this.showError = !this.valid
      this.showValid = !this.showError
      this.validationError = 'This field is required.'
    },
  },

  computed: {
    valid: function () {
      return this.optional || this.selections.length > 0
    },
  },
}
