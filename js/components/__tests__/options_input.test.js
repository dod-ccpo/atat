import { mount } from '@vue/test-utils'

import optionsinput from '../options_input'

import { makeTestWrapper } from '../../test_utils/component_test_helpers'

const SelectWrapperComponent = makeTestWrapper({
  components: {
    optionsinput,
  },
  templatePath: 'select_input_template.html',
  data: function () {
    const { initialvalue, optional } = this.initialData
    return { initialvalue, optional }
  },
})

describe('SelectInput Renders Correctly', () => {
  it('Should initialize checked', () => {
    const wrapper = mount(SelectWrapperComponent, {
      propsData: {
        name: 'testCheck',
        initialData: {
          initialvalue: 'b',
          optional: true,
        },
      },
    })
    expect(wrapper.find('.usa-input select').element.value).toBe('b')
  })

  it('Should initialize unchecked', () => {
    const wrapper = mount(SelectWrapperComponent, {
      propsData: {
        name: 'testCheck',
        initialData: {
          initialvalue: '',
          optional: false,
        },
      },
    })
    expect(wrapper.find('.usa-input select').element.value).toBe('')
  })

  it('Should be considered invalid if default is re-selected', async () => {
    const wrapper = mount(SelectWrapperComponent, {
      propsData: {
        name: 'testCheck',
        initialData: {
          initialvalue: '',
          optional: false,
        },
      },
    })

    await wrapper.find('select#selectfield').trigger('change')

    expect(wrapper.contains('.usa-input--error')).toBe(true)
    expect(wrapper.contains('.usa-input--success')).toBe(false)
  })

  it('Should be considered valid if value is selected', async () => {
    const wrapper = mount(SelectWrapperComponent, {
      propsData: {
        name: 'testCheck',
        initialData: {
          initialvalue: '',
          optional: false,
        },
      },
    })

    const selectField = wrapper.find('select#selectfield')
    await wrapper.find('option[value="a"]').setSelected()
    await selectField.trigger('change')

    expect(wrapper.contains('.usa-input--error')).toBe(false)
    expect(wrapper.contains('.usa-input--success')).toBe(true)
  })
})

const RadioWrapperComponent = makeTestWrapper({
  components: {
    optionsinput,
  },
  templatePath: 'radio_input_template.html',
  data: function () {
    const { initialvalue, optional } = this.initialData
    return { initialvalue, optional }
  },
})

describe('RadioInput Renders Correctly', () => {
  it('Should initialize checked', () => {
    const wrapper = mount(RadioWrapperComponent, {
      propsData: {
        name: 'testCheck',
        initialData: {
          initialvalue: 'b',
          optional: true,
        },
      },
    })
    expect(wrapper.find('.usa-input input[value="a"]').element.checked).toBe(
      false
    )
    expect(wrapper.find('.usa-input input[value="b"]').element.checked).toBe(
      true
    )
  })

  it('Should initialize unchecked', () => {
    const wrapper = mount(RadioWrapperComponent, {
      propsData: {
        name: 'testCheck',
        initialData: {
          initialvalue: '',
          optional: false,
        },
      },
    })
    expect(wrapper.find('.usa-input input').element.checked).toBe(false)
  })

  it('Should be considered invalid if default is re-selected', async () => {
    const wrapper = mount(RadioWrapperComponent, {
      propsData: {
        name: 'testCheck',
        initialData: {
          initialvalue: '',
          optional: false,
        },
      },
    })

    expect(wrapper.vm.$children[0].valid).toBe(false)
  })

  it('Should be considered valid if value is selected', async () => {
    const wrapper = mount(RadioWrapperComponent, {
      propsData: {
        name: 'testCheck',
        initialData: {
          initialvalue: '',
          optional: false,
        },
      },
    })

    await wrapper.findAll('input[type="radio"]').at(0).setChecked()

    expect(wrapper.contains('.usa-input--error')).toBe(false)
    expect(wrapper.contains('.usa-input--success')).toBe(true)
  })
})
