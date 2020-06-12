import FormMixin from '../../../mixins/form'
import textinput from '../../text_input'
import * as R from 'ramda'

const createEnvironment = (name) => ({ name })

export default {
  name: 'application-environments',

  mixins: [FormMixin],

  components: {
    textinput,
  },

  props: {
    initialData: {
      type: Object,
      default: () => ({}),
    },
  },

  data: function () {
    const { environment_names, name } = this.initialData

    const environments = (environment_names.length > 0
      ? environment_names
      : ['Development', 'Testing', 'Staging', 'Production']
    ).map(createEnvironment)

    return {
      validations: [
        {
          func: this.hasEnvironments,
          message: 'Provide at least one environment name.',
        },
        {
          func: this.environmentsHaveNames,
          message: 'Environment names cannot be empty.',
        },
        {
          func: this.envNamesAreUnique,
          message: 'Environment names must be unique.',
        },
      ],
      errors: [],
      environments,
      name,
      changed: true,
    }
  },

  mounted: function () {
    this.validate()
  },

  methods: {
    addEnvironment: function (_event) {
      this.changed = false
      this.environments.push(createEnvironment(''))
    },

    removeEnvironment: function (index) {
      if (this.environments.length > 1) {
        this.environments.splice(index, 1)
      }
      this.validate()
    },

    validate: function () {
      // Only take first error message
      this.errors = R.pipe(
        R.map((validation) =>
          !validation.func() ? validation.message : undefined
        ),
        R.filter(Boolean),
        R.take(1)
      )(this.validations)
      this.invalid = this.errors.length > 0
    },

    hasEnvironments: function () {
      return (
        this.environments.length > 0 &&
        this.environments.some((e) => e.name !== '')
      )
    },

    environmentsHaveNames: function () {
      if (this.environments.length > 1) {
        // only want to display this error if we have multiple envs and one or
        // more do not have names
        return this.environments.every(
          (e) => !e.name.match(/^\s+$/) && e.name !== ''
        )
      } else {
        return true
      }
    },

    envNamesAreUnique: function () {
      const names = this.environments.map((e) => e.name)
      return names.every((n, index) => names.indexOf(n) === index)
    },

    onInput: function (e) {
      this.changed = true
      this.validate()
    },
  },
}
