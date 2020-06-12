import { mount } from '@vue/test-utils'
import multicheckboxinput from '../multi_checkbox_input'
import { makeTestWrapper } from '../../test_utils/component_test_helpers'

const WrapperComponent = makeTestWrapper({
  components: {
    multicheckboxinput,
  },
  templatePath: 'multi_checkbox_input_template.html',
  data: function () {
    const { initialvalue, optional } = this.initialData
    return { initialvalue, optional }
  },
})

describe('MultiCheckboxInput Renders Correctly', () => {
  it('Should initialize unchecked and with no validation showing', () => {
    const wrapper = mount(WrapperComponent, {
      propsData: {
        name: 'testCheck',
        initialData: {
          initialvalue: [],
        },
      },
    })
    expect(wrapper.contains('.usa-input--success')).toBe(false)
    expect(wrapper.contains('.usa-input--error')).toBe(false)
    expect(wrapper.find('.usa-input input[value="a"]').element.checked).toBe(
      false
    )
    expect(wrapper.find('.usa-input input[value="b"]').element.checked).toBe(
      false
    )
  })

  it('Should initialize with "a" checked', () => {
    const wrapper = mount(WrapperComponent, {
      propsData: {
        name: 'testCheck',
        initialData: {
          initialvalue: ['a'],
        },
      },
    })
    expect(wrapper.find('.usa-input input[value="a"]').element.checked).toBe(
      true
    )
    expect(wrapper.find('.usa-input input[value="b"]').element.checked).toBe(
      false
    )
  })
})

describe('Multicheckbox shows validation states correctly', () => {
  it('Should be valid when any checkbox is clicked', () => {
    const wrapper = mount(WrapperComponent, {
      propsData: {
        name: 'testCheck',
        initialData: { initialvalue: [] },
      },
    })
    wrapper.find('.usa-input input[value="a"]').setChecked()
    expect(wrapper.contains('.usa-input--success')).toBe(true)
    expect(wrapper.contains('.usa-input--error')).toBe(false)
  })

  it('Should be invalid when no checkboxes are checked', () => {
    const wrapper = mount(WrapperComponent, {
      propsData: {
        name: 'testCheck',
        initialData: {
          initialvalue: [],
        },
      },
    })

    // Check and then uncheck a checkbox
    const checkboxA = wrapper.find('.usa-input input[value="a"]')
    checkboxA.setChecked()
    checkboxA.setChecked(false)

    expect(wrapper.contains('.usa-input--error')).toBe(true)
    expect(wrapper.contains('.usa-input--success')).toBe(false)
  })

  it('Should be valid when no checkboxes are checked but it is optional', () => {
    const wrapper = mount(WrapperComponent, {
      propsData: {
        name: 'testCheck',
        initialData: { initialvalue: [], optional: true },
      },
    })

    // Check and then uncheck a checkbox
    const checkboxA = wrapper.find('.usa-input input[value="a"]')
    checkboxA.setChecked()
    checkboxA.setChecked(false)

    expect(wrapper.contains('.usa-input--error')).toBe(false)
    expect(wrapper.contains('.usa-input--success')).toBe(true)
  })
})
