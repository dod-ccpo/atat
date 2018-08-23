export default {
  name: 'toggler',

  props: {
    defaultVisible: {
      type: Boolean,
      default: () => false
    }
  },

  data: function () {
    return {
      isVisible: this.defaultVisible
    }
  },

  render: function (createElement) {
    return createElement( this.$vnode.data.tag, [
      this.$scopedSlots.default({
        isVisible: this.isVisible,
        toggle: this.toggle
      })
    ])
  },

  methods: {
    toggle: function (e) {
      this.isVisible = !this.isVisible
    }
  }
}
