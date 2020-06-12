import Accordion from './accordion'

export default {
  name: 'accordion-list',

  components: {
    Accordion,
  },

  methods: {
    handleClick: function (e) {
      e.preventDefault()
      this.$children.forEach((el) => el.collapse())
    },
  },
}
