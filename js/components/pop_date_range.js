import { format } from 'date-fns'

import { emitEvent } from '../lib/emitters'

import DateSelector from './date_selector'

const START_DATE = 'start_date'
const END_DATE = 'end_date'

export default {
  name: 'pop-date-range',

  components: {
    DateSelector,
  },

  props: {
    initialMinStartDate: String,
    initialMaxEndDate: String,
    initialStartDate: {
      type: String,
      default: null,
    },
    initialEndDate: {
      type: String,
      default: null,
    },
    clinIndex: Number,
  },

  data: function() {
    let start = !!this.initialStartDate
      ? new Date(this.initialStartDate)
      : false
    let contractStart = new Date(this.initialMinStartDate)
    let minEndDate = start && start > contractStart ? start : contractStart

    let end = !!this.initialEndDate ? new Date(this.initialEndDate) : false
    let contractEnd = new Date(this.initialMaxEndDate)
    let maxStartDate = end && end < contractEnd ? end : contractEnd

    // the maxStartDate and minEndDate change based on user input:
    // the latest date the start can be is the PoP end date
    // the earliest date the end can be is the PoP start date
    // if the form is initialized with out a PoP, the maxStartDate and minEndDate
    // default to the contract dates
    return {
      maxStartDate: maxStartDate,
      minEndDate: minEndDate,
      contractStart: contractStart,
      contractEnd: contractEnd,
    }
  },

  methods: {
    handleDateChange: function(event) {
      if (event.name.includes(START_DATE) && event.valid) {
        let date = new Date(event.value)
        this.minEndDate = this.calcMinEndDate(date)
      } else if (event.name.includes(END_DATE) && event.valid) {
        let date = new Date(event.value)
        this.maxStartDate = this.calcMaxStartDate(date)
      }
    },

    calcMaxStartDate: function(date) {
      if (!!date && date < this.contractEnd) {
        return date
      } else {
        return this.maxStartDate
      }
    },

    calcMinEndDate: function(date) {
      if (!!date && date > this.contractStart) {
        return date
      } else {
        return this.minEndDate
      }
    },

    handleFieldMount: function(event) {
      if (event.parent_uid === this._uid) {
        emitEvent('field-mount', this, event)
      }
    },
  },

  computed: {
    maxStartProp: function() {
      return format(this.maxStartDate, 'YYYY-MM-DD')
    },

    minEndProp: function() {
      return format(this.minEndDate, 'YYYY-MM-DD')
    },
  },

  created: function() {
    this.$root.$on('field-mount', this.handleFieldMount)
  },
}
