import { format, isWithinRange, addMonths, isSameMonth, getMonth } from 'date-fns'
import { abbreviateDollars, formatDollars } from '../../lib/dollars'

const TOP_OFFSET = 20
const BOTTOM_OFFSET = 70
const CHART_HEIGHT = 360

export default {
  name: 'budget-chart',
  props: {
    currentMonth: String,
    expirationDate: String,
    months: Object,
    budget: String
  },

  data: function () {
    const heightScale = this.budget / (CHART_HEIGHT - TOP_OFFSET - BOTTOM_OFFSET)
    return {
      numMonths: 10,
      focusedMonthPosition: 4,
      height: CHART_HEIGHT,
      heightScale,
      budgetHeight: CHART_HEIGHT - BOTTOM_OFFSET - (this.budget / heightScale),
      baseHeight: CHART_HEIGHT - BOTTOM_OFFSET,
      width: 0,
      displayedMonths: [],
      spendPath: '',
      projectedPath: '',
      displayBudget: formatDollars(parseFloat(this.budget))
    }
  },

  mounted: function () {
    this._setDisplayedMonths()
    this._setMetrics()
    addEventListener('load', this._setMetrics)
    addEventListener('resize', this._setMetrics)
  },

  methods: {
    _setMetrics: function () {
      this.width = this.$refs.panel.clientWidth
      this.spendPath = ''
      this.projectedPath = ''

      let lastSpend = 0
      let lastSpendPoint = ''

      for (let i = 0; i < this.numMonths; i++) {
        const { metrics, budget, rollingAverage, cumulativeTotal } = this.displayedMonths[i]
        const blockWidth = (this.width / this.numMonths)
        const blockX = blockWidth * i
        const spend = budget && budget.spend
          ? budget.spend
          : rollingAverage
        const barHeight = spend / this.heightScale
        lastSpend = spend
        const cumulativeY = this.height - (cumulativeTotal / this.heightScale) - BOTTOM_OFFSET
        const cumulativeX = blockX + blockWidth/2
        const cumulativePoint = `${cumulativeX} ${cumulativeY}`

        this.displayedMonths[i].metrics = Object.assign(metrics, {
          blockWidth,
          blockX,
          barHeight,
          barWidth: 30,
          barX: blockX + (blockWidth/2 - 15),
          barY: this.height - barHeight - BOTTOM_OFFSET,
          cumulativeR: 2.5,
          cumulativeY,
          cumulativeX
        })

        if (budget && budget.spend) {
          this.spendPath += this.spendPath === '' ? 'M' : ' L'
          this.spendPath += cumulativePoint
          lastSpendPoint = cumulativePoint

        } else if (lastSpendPoint !== '') {
          this.projectedPath += this.projectedPath === '' ? `M${lastSpendPoint} L` : ' L'
          this.projectedPath += cumulativePoint
        }
      }
    },

    _setDisplayedMonths: function () {
      const [month, year] = this.currentMonth.split('/')
      const [expYear, expMonth, expDate] = this.expirationDate.split('-') // assumes format 'YYYY-MM-DD'
      const monthsRange = []
      const monthsBack = this.focusedMonthPosition + 1
      const monthsForward = this.numMonths - this.focusedMonthPosition - 1

      // currently focused date
      const current = new Date(year, month)

      // starting date of the chart
      const start = addMonths(current, -monthsBack)

      // ending date of the chart
      const end = addMonths(start, this.numMonths + 1)

      // expiration date
      const expires = new Date(expYear, expMonth-1, expDate)

      // is the expiration date within the displayed date range?
      const expirationWithinRange = isWithinRange(expires, start, end)

      let rollingAverage = 0
      let cumulativeTotal = 0

      for (let i = 0; i < this.numMonths; i++) {
        const date = addMonths(start, i)
        const dateMinusOne = addMonths(date, -1)
        const dateMinusTwo = addMonths(date, -2)
        const dateMinusThree = addMonths(date, -3)

        const index = format(date, 'MM/YYYY')
        const indexMinusOne = format(dateMinusOne, 'MM/YYYY')
        const indexMinusTwo = format(dateMinusTwo, 'MM/YYYY')
        const indexMinusThree = format(dateMinusThree, 'MM/YYYY')

        const budget = this.months[index] || null
        const spendAmount = budget ? budget.spend : rollingAverage
        const spendMinusOne = this.months[indexMinusOne] ? this.months[indexMinusOne].spend : rollingAverage
        const spendMinusTwo = this.months[indexMinusTwo] ? this.months[indexMinusTwo].spend : rollingAverage
        const spendMinusThree = this.months[indexMinusThree] ? this.months[indexMinusThree].spend : rollingAverage

        const isExpirationMonth = isSameMonth(date, expires)

        if (budget && budget.cumulative) {
          cumulativeTotal = budget.cumulative
        } else {
          cumulativeTotal += spendAmount
        }

        rollingAverage = (
            spendAmount
          + spendMinusOne
          + spendMinusTwo
          + spendMinusThree
          ) / 4

        monthsRange.push({
          budget,
          rollingAverage,
          cumulativeTotal,
          isExpirationMonth,
          spendAmount: formatDollars(spendAmount),
          abbreviatedSpend: abbreviateDollars(spendAmount),
          cumulativeAmount: formatDollars(cumulativeTotal),
          abbreviatedCumulative: abbreviateDollars(cumulativeTotal),
          date: {
            monthIndex: format(date, 'M'),
            month: format(date, 'MMM'),
            year: format(date,'YYYY')
          },
          showYear: isExpirationMonth || (i === 0) || getMonth(date) === 0,
          isHighlighted: this.currentMonth === index,
          metrics: {
            blockWidth: 0,
            blockX: 0,
            barHeight: 0,
            barWidth: 0,
            barX: 0,
            barY: 0,
            cumulativeY: 0,
            cumulativeX: 0,
            cumulativeR: 0
          }
        })

      }
      this.displayedMonths = monthsRange
    }
  }
}
