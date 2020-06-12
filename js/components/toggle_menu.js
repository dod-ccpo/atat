import ToggleMixin from '../mixins/toggle'

export default {
  name: 'toggleMenu',

  mixins: [ToggleMixin],

  props: {
    defaultVisible: {
      type: Boolean,
      default: false,
    },
  },

  methods: {
    toggle: function (e) {
      if (this.$el.contains(e.target)) {
        this.isVisible = !this.isVisible
      } else {
        this.isVisible = false
      }
    },
  },

  mounted: function () {
    document.addEventListener('click', this.toggle)
  },

  beforeDestroy: function () {
    document.removeEventListener('click', this.toggle)
  },
}
