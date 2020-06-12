import { mount } from '@vue/test-utils'

import textinput from '../text_input'

import { makeTestWrapper } from '../../test_utils/component_test_helpers'

const ToNumberWrapperComponent = makeTestWrapper({
  components: {
    textinput,
  },
  templatePath: 'text_input_to_number.html',
  data: function () {
    const { validation, initialValue } = this.initialData
    return { validation, initialValue }
  },
})

describe('TextInput Validates Correctly', () => {
  describe('taskOrderNumber validator', () => {
    it('Should initialize with the validator and no validation icon', () => {
      const wrapper = mount(ToNumberWrapperComponent, {
        propsData: {
          name: 'testTextInput',
          initialData: {
            validation: 'taskOrderNumber',
          },
        },
      })
      expect(wrapper.contains('.usa-input--success')).toBe(false)
      expect(wrapper.contains('.usa-input--error')).toBe(false)
      expect(wrapper.contains('.usa-input--validation--taskOrderNumber')).toBe(
        true
      )
    })

    it('Should allow valid TO numbers', () => {
      const wrapper = mount(ToNumberWrapperComponent, {
        propsData: {
          name: 'testTextInput',
          initialData: {
            validation: 'taskOrderNumber',
          },
        },
      })

      var textInputField = wrapper.find('input[id="number"]')
      var hiddenField = wrapper.find('input[name="number"]')
      const validToNumbers = [
        '12345678901234567',
        '1234567890123',
        'abc1234567890', // pragma: allowlist secret
        'abc-1234567890',
        'DC12-123-1234567890',
        'fg34-987-1234567890',
      ]

      for (const number of validToNumbers) {
        // set value to be a valid TO number
        textInputField.setValue(number)
        // manually trigger change event in hidden fields
        hiddenField.trigger('change')
        // check for validation classes
        expect(wrapper.contains('.usa-input--success')).toBe(true)
        expect(wrapper.contains('.usa-input--error')).toBe(false)
      }
    })

    it('Should not allow invalid TO numbers', () => {
      const wrapper = mount(ToNumberWrapperComponent, {
        propsData: {
          name: 'testTextInput',
          initialData: {
            validation: 'taskOrderNumber',
          },
        },
      })

      var textInputField = wrapper.find('input[id="number"]')
      var hiddenField = wrapper.find('input[name="number"]')
      const invalidToNumbers = [
        '1234567890',
        '12345678901234567890', // pragma: allowlist secret
        '123:4567890123',
        '123_1234567890',
      ]

      for (const number of invalidToNumbers) {
        // set value to be a valid TO number
        textInputField.setValue(number)
        // manually trigger change event in hidden fields
        hiddenField.trigger('change')
        // check for validation classes
        expect(wrapper.contains('.usa-input--success')).toBe(false)
        expect(wrapper.contains('.usa-input--error')).toBe(true)
      }
    })
  })
})
