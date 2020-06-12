import { emitFieldChange } from '../lib/emitters'

export default {
  name: 'checkboxinput',

  props: {
    name: String,
    initialChecked: Boolean,
    optional: Boolean,
  },

  data: function () {
    return {
      isChecked: this.initialChecked,
    }
  },

  methods: {
    onInput: function () {
      emitFieldChange(this)
    },
  },

  computed: {
    valid: function () {
      return this.optional || this.isChecked
    },
  },
}
