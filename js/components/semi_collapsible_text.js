export default {
  name: 'semi-collapsible-text',

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
