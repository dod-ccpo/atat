import { format } from 'date-fns'

export default {
  name: 'local-datetime',

  props: {
    timestamp: String,
    format: {
      type: String,
      default: 'MMM D YYYY H:mm',
    },
  },

  computed: {
    displayTime: function () {
      return format(this.timestamp, this.format)
    },
  },

  template: '<time v-bind:datetime="timestamp">{{ displayTime }}</time>',
}
