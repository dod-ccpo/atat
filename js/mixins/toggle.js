export default {
  data: function () {
    return {
      isVisible: this.defaultVisible,
    }
  },

  render: function (createElement) {
    return createElement(this.$vnode.data.tag, [
      this.$scopedSlots.default({
        isVisible: this.isVisible,
        toggle: this.toggle,
      }),
    ])
  },

  methods: {
    toggle: function (e) {
      e.preventDefault()
      e.stopPropagation()
      this.isVisible = !this.isVisible
    },
  },
}
