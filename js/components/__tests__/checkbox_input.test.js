import { mount } from '@vue/test-utils'

import checkboxinput from '../checkbox_input'

import { makeTestWrapper } from '../../test_utils/component_test_helpers'

const WrapperComponent = makeTestWrapper({
  components: {
    checkboxinput,
  },
  templatePath: 'checkbox_input_template.html',
  data: function () {
    return { initialvalue: this.initialData }
  },
})

describe('CheckboxInput Renders Correctly', () => {
  it('Should initialize checked', () => {
    const wrapper = mount(WrapperComponent, {
      propsData: {
        name: 'testCheck',
        initialData: true,
      },
    })
    expect(wrapper.find('.usa-input input').element.checked).toBe(true)
  })

  it('Should initialize unchecked', () => {
    const wrapper = mount(WrapperComponent, {
      propsData: {
        name: 'testCheck',
        initialData: false,
      },
    })
    expect(wrapper.find('.usa-input input').element.checked).toBe(false)
  })
})
