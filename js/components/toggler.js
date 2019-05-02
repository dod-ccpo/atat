import FormMixin from '../mixins/form'
import textinput from './text_input'

export default {
  name: 'toggler',

  mixins: [FormMixin],

  props: {
    initialSelectedSection: String,
  },

  components: {
    textinput,
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
