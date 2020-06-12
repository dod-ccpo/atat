import FormMixin from '../../mixins/form'
import textinput from '../text_input'

export default {
  name: 'new-environment',

  mixins: [FormMixin],

  components: {
    textinput,
  },

  data: function () {
    return {
      open: false,
    }
  },

  methods: {
    toggle: function () {
      this.open = !this.open
    },
  },
}
