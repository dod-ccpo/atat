import classes from '../styles/atat.scss'
import Vue from 'vue/dist/vue'
import VTooltip from 'v-tooltip'

import textinput from './components/text_input'

Vue.use(VTooltip)


const app = new Vue({
  el: '#app-root',
  components: {
    textinput
  },
  methods: {
    closeModal: function(name) {
      this.modals[name] = false
    },
    openModal: function (name) {
      this.modals[name] = true
    }
  },
  data: function() {
    return {
      modals: {
        styleguideModal: false,
        pendingFinancialVerification: false,
      }
    }
  },
  mounted: function() {
    const modalOpen = document.querySelector("#modalOpen");
    if (modalOpen) {
      const modal = modalOpen.getAttribute("data-modal");
      this.modals[modal] = true;
    }
  }
})
