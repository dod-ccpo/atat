export default {
  name: 'save_as_draft',

  props: {
    is_draft_initial: Boolean
  },

  data: function() {
    return {
      is_draft: this.is_draft_initial
    }
  },

  updated: function() {
    document.getElementById('form').submit();
  },

  methods: {
    save: function() {
      this.is_draft = true;
    }
  }
}
