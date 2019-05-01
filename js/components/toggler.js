import FormMixin from '../mixins/form'
import textinput from './text_input'
import optionsinput from './options_input'

export default {
  name: 'toggler',

  mixins: [FormMixin],

  components: {
    textinput,
    optionsinput,
  },

  data: function() {
    return {
      selectedSection: this.initialSelectedSection,
    }
  },

  methods: {
    toggleSection: function(sectionName) {
      if (this.selectedSection === sectionName) {
        this.selectedSection = null
      } else {
        this.selectedSection = sectionName
      }
    },
  },
}
