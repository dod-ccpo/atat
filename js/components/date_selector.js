import Vue from 'vue'
import { getDaysInMonth } from 'date-fns'
import { emitFieldChange } from '../lib/emitters'

let paddedNumber = function (number) {
  if ((number + '').length === 1) {
    return `0${number}`
  } else {
    return number
  }
}

export default {
  name: 'date-selector',

  props: {
    initialday: { type: String },
    initialmonth: { type: String },
    initialyear: { type: String },
    mindate: { type: String },
    maxdate: { type: String },
    minrange: { type: String },
    maxrange: { type: String },
    nameTag: { type: String },
    optional: {
      type: Boolean,
      default: true,
    },
  },

  data: function () {
    return {
      day: this.initialday,
      month: this.initialmonth,
      year: this.initialyear,
      name: this.nameTag,
    }
  },

  watch: {
    month(newMonth, oldMonth) {
      if (!!newMonth && newMonth.length > 2) {
        this.month = oldMonth
      } else {
        this.month = newMonth
      }
    },

    day(newDay, oldDay) {
      if (!!newDay && newDay.length > 2) {
        this.day = oldDay
      } else {
        this.day = newDay
      }
    },

    year(newYear, oldYear) {
      if (!!newYear && newYear.length > 4) {
        this.year = oldYear
      } else {
        this.year = newYear
      }
    },
  },

  computed: {
    formattedDate: function () {
      let day = paddedNumber(this.day)
      let month = paddedNumber(this.month)

      if (!day || !month || !this.year) {
        return null
      }

      return `${month}/${day}/${this.year}`
    },

    isMonthValid: function () {
      const month = parseInt(this.month)
      return month >= 1 && month <= 12
    },

    isDayValid: function () {
      const day = parseInt(this.day)
      return day >= 1 && day <= this.daysMaxCalculation
    },

    isYearValid: function () {
      let valid
      const minYear = this.mindate ? parseInt(this.mindate) : null
      const maxYear = this.maxdate ? parseInt(this.maxdate) : null

      if (minYear && maxYear) {
        valid = this.year >= minYear && this.year <= maxYear
      } else {
        valid = parseInt(this.year) >= 1
      }

      return valid
    },

    isWithinDateRange: function () {
      if (
        this.minDateParsed !== null &&
        this.minDateParsed >= this.dateParsed
      ) {
        return false
      }

      if (
        this.maxDateParsed !== null &&
        this.maxDateParsed <= this.dateParsed
      ) {
        return false
      }

      return true
    },

    isDateValid: function () {
      return (
        !!this.day &&
        !!this.month &&
        !!this.year &&
        this.isDayValid &&
        this.isMonthValid &&
        this.isYearValid &&
        this.isWithinDateRange
      )
    },

    isDateComplete: function () {
      return !!this.day && !!this.month && !!this.year && this.year > 999
    },

    daysMaxCalculation: function () {
      switch (parseInt(this.month)) {
        case 2: // February
          if (this.year) {
            return getDaysInMonth(new Date(this.year, this.month - 1))
          } else {
            return 29
          }

        case 4: // April
        case 6: // June
        case 9: // September
        case 11: // November
          return 30

        default:
          // All other months, or null, go with 31
          return 31
      }
    },

    minError: function () {
      if (this.isDateComplete) {
        return this.minDateParsed >= this.dateParsed
      }

      return false
    },

    maxError: function () {
      if (this.isDateComplete) {
        return this.maxDateParsed <= this.dateParsed
      }

      return false
    },

    outsideRange: function () {
      if (!!this.maxrange && !!this.minrange && this.isDateComplete) {
        return (
          this.dateParsed < this.minRangeParsed ||
          this.dateParsed > this.maxRangeParsed
        )
      }
    },

    maxDateParsed: function () {
      let _maxdate = this.maxdate ? Date.parse(this.maxdate) : null
      return _maxdate
    },

    minDateParsed: function () {
      let _mindate = this.mindate ? Date.parse(this.mindate) : null
      return _mindate
    },

    maxRangeParsed: function () {
      let _maxrange = this.maxrange ? Date.parse(this.maxrange) : null
      return _maxrange
    },

    minRangeParsed: function () {
      let _minrange = this.minrange ? Date.parse(this.minrange) : null
      return _minrange
    },

    dateParsed: function () {
      return Date.UTC(this.year, this.month - 1, this.day)
    },

    valid: function () {
      return this.isDateValid
    },
  },

  methods: {
    onInput: function () {
      emitFieldChange(this, {
        value: this.formattedDate,
        name: this.name,
        valid: this.isDateValid,
      })
    },
  },

  render: function (createElement) {
    return createElement('p', 'Please implement inline-template')
  },
}
