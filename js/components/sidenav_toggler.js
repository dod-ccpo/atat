import ExpandSidenavMixin from '../mixins/expand_sidenav'
import ToggleMixin from '../mixins/toggle'

export default {
  name: 'sidenav-toggler',

  mixins: [ExpandSidenavMixin, ToggleMixin],

  mounted: function() {
    this.$parent.$emit('sidenavToggle', this.isVisible)
  },

  methods: {
    toggle: function(e) {
      e.preventDefault()
      this.isVisible = !this.isVisible
      document.cookie = this.cookieName + '=' + this.isVisible + '; path=/'
      this.$parent.$emit('sidenavToggle', this.isVisible)
    },
  },
}
