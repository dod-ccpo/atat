export default {
  name: 'delete-confirmation',

  props: {
    confirmationText: {
      type: String,
      default: 'delete',
    },
  },

  data: function () {
    return {
      deleteText: '',
    }
  },

  computed: {
    valid: function () {
      return this.deleteText.toLowerCase() === this.confirmationText
    },
  },
}
