export default {
  name: 'optionsinput',

  props: {
    name: String,
    initialErrors: {
      type: Array,
      default: () => [],
    },
    initialValue: String,
  },

  data: function() {
    const showError = (this.initialErrors && this.initialErrors.length) || false
    return {
      showError: showError,
      showValid: !showError && !!this.initialValue,
      validationError: this.initialErrors.join(' '),
    }
  },

  methods: {
    onInput: function(e) {
      this.$root.$emit('field-change', {
        value: e.target.value,
        name: this.name,
      })
      this.showError = false
      this.showValid = true
    },
  },
}
