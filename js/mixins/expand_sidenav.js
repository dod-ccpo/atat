import { sidenavCookieName } from '../lib/constants'

export default {
  props: {
    defaultVisible: {
      type: Boolean,
      default: function () {
        if (document.cookie.match(sidenavCookieName)) {
          return !!document.cookie.match(sidenavCookieName + ' *= *true')
        } else {
          return true
        }
      },
    },
  },
}
