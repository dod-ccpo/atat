import inputValidations from '../lib/input_validations'
import TextInputMixin from '../mixins/text_input_mixin'

export default {
  name: 'clindollaramount',

  mixins: [TextInputMixin],

  props: {
    fundingValid: Boolean,
  },

  computed: {
    rawValue: function () {
      return this._rawValue(this.value)
    },
    showFundingError: function () {
      return this.showError || !this.fundingValid
    },
    showFundingValid: function () {
      return this.showValid && this.fundingValid
    },
  },
  watch: {
    fundingValid: function (oldVal, newVal) {
      this._checkIfValid({ value: this.value, invalidate: true })
    },
  },

  methods: {
    _validate: function (value) {
      const rawValue = this._rawValue(value)
      if (rawValue < 0 || rawValue > 1000000000 || !this.fundingValid) {
        return false
      }
      return inputValidations[this.validation].match.test(rawValue)
    },
  },
}
