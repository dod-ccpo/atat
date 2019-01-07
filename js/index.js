import 'svg-innerhtml'
import 'babel-polyfill'

import classes from '../styles/atat.scss'
import Vue from 'vue/dist/vue'
import VTooltip from 'v-tooltip'

import optionsinput from './components/options_input'
import multicheckboxinput from './components/multi_checkbox_input'
import textinput from './components/text_input'
import checkboxinput from './components/checkbox_input'
import DetailsOfUse from './components/forms/details_of_use'
import poc from './components/forms/poc'
import cor from './components/forms/cor'
import financial from './components/forms/financial'
import toggler from './components/toggler'
import NewApplication from './components/forms/new_application'
import EditEnvironmentRole from './components/forms/edit_environment_role'
import EditApplicationRoles from './components/forms/edit_application_roles'
import funding from './components/forms/funding'
import Modal from './mixins/modal'
import selector from './components/selector'
import BudgetChart from './components/charts/budget_chart'
import SpendTable from './components/tables/spend_table'
import TaskOrderList from './components/tables/task_order_list.js'
import CcpoApproval from './components/forms/ccpo_approval'
import MembersList from './components/members_list'
import LocalDatetime from './components/local_datetime'
import RequestsList from './components/requests_list'
import ConfirmationPopover from './components/confirmation_popover'
import savedraft from './components/savedraft'

Vue.config.productionTip = false

Vue.use(VTooltip)

Vue.mixin(Modal)

const app = new Vue({
  el: '#app-root',
  components: {
    toggler,
    optionsinput,
    multicheckboxinput,
    savedraft,
    textinput,
    checkboxinput,
    DetailsOfUse,
    poc,
    cor,
    financial,
    NewApplication,
    selector,
    BudgetChart,
    SpendTable,
    TaskOrderList,
    CcpoApproval,
    MembersList,
    LocalDatetime,
    EditEnvironmentRole,
    EditApplicationRoles,
    RequestsList,
    ConfirmationPopover,
    funding,
  },

  mounted: function() {
    this.$on('modalOpen', isOpen => {
      if (isOpen) {
        document.body.className += ' modal-open'
      } else {
        document.body.className = document.body.className.replace(' modal-open', '')
      }
    })

    const modalOpen = document.querySelector("#modalOpen")

    if (modalOpen) {
      const modal = modalOpen.getAttribute("data-modal")
      this.openModal(modal)
    }
  },
  delimiters: ['!{', '}']
})
