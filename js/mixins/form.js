export default {
  props: {
    initialSelectedSection: String,
    hasChanges: {
      type: Boolean,
      default: false,
    },
  },

  mounted: function() {
    this.$root.$on('field-change', this.handleFieldChange)
  },

  created: function() {
    this.$root.$on('field-mount', this.handleFieldMount)
  },

  methods: {
    handleFieldChange: function(event) {
      const { value, name, valid, parent_uid, watch } = event
      if (typeof this.fields[name] !== undefined) {
        this.fields[name] = valid
        if (parent_uid === this._uid || watch) {
          this.changed = true
        }
      }

      this.validateForm()
    },

    handleFieldMount: function(event) {
      if (
        event.parent_uid === this._uid ||
        this.$children.some(c => c._uid === event.parent_uid)
      ) {
        const { name, optional, valid } = event
        this.fields[name] = optional || valid
        const formValid = this.validateForm()
        this.invalid = !formValid
      }
    },

    validateForm: function() {
      const valid = !Object.values(this.fields).some(field => field === false)
      this.invalid = !valid
      return valid
    },

    handleSubmit: function(event) {
      if (this.invalid) {
        event.preventDefault()
      }
    },
  },

  computed: {
    canSave: function() {
      const formValid = !this.invalid

      if (formValid) {
        return true
      } else if (this.changed && formValid) {
        return true
      } else {
        return false
      }
    },
  },

  data: function() {
    return {
      changed: this.hasChanges,
      fields: {},
      invalid: true,
    }
  },
}
