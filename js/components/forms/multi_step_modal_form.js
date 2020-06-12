import FormMixin from '../../mixins/form'
import textinput from '../text_input'
import optionsinput from '../options_input'
import checkboxinput from '../checkbox_input'
import Modal from '../../mixins/modal'
import toggler from '../toggler'

export default {
  name: 'multi-step-modal-form',

  mixins: [FormMixin],

  components: {
    toggler,
    Modal,
    textinput,
    optionsinput,
    checkboxinput,
  },

  props: {
    steps: Number,
  },

  data: function () {
    return {
      step: 0,
    }
  },

  mounted: function () {
    this.$root.$on('modalOpen', this.handleModalOpen)
  },

  methods: {
    next: function () {
      this.submitted = true
      if (this.validateFields()) {
        this.step += 1
        this.submitted = false
      }
    },
    previous: function () {
      this.step -= 1
    },
    goToStep: function (step) {
      if (this.validateFields()) {
        this.step = step
      }
    },
    handleModalOpen: function (_bool) {
      this.step = 0
    },
    _onLastPage: function () {
      return this.step === this.steps - 1
    },
    handleSubmit: function (e) {
      if (this._onLastPage) {
        this.submitted = true
      }

      if (!this.validateFields() || !this._onLastPage()) {
        e.preventDefault()
        this.next()
      }
    },
  },
}
