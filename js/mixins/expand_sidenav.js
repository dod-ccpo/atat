export default {
  props: {
    cookieName: 'expandSidenav',
    defaultVisible: {
      type: Boolean,
      default: function() {
        if (document.cookie.match(this.cookieName)) {
          return !!document.cookie.match(this.cookieName + ' *= *true')
        } else {
          return true
        }
      },
    },
  },
}
