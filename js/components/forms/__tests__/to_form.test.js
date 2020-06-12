import { mount } from '@vue/test-utils'

import toForm from '../to_form'
import clinFields from '../../clin_fields'

import { makeTestWrapper } from '../../../test_utils/component_test_helpers'

const TOFormWrapper = makeTestWrapper({
  components: { toForm },
  templatePath: 'to_form.html',
})

describe('TOForm Test', () => {
  it('should allow users to add new CLINs', () => {
    const wrapper = mount(TOFormWrapper, {
      propsData: {
        initialData: {},
      },
    })
    expect(wrapper.findAll(clinFields).length).toBe(1)
    wrapper.find('#add-clin').trigger('click')
    expect(wrapper.findAll(clinFields).length).toBe(2)
  })

  it('should not enable the save button until the form is complete and valid', () => {
    const wrapper = mount(TOFormWrapper, {
      propsData: {
        initialData: {},
      },
    })

    const submit = wrapper.find('input[type=submit]')
    function expectSubmitIsDisabled() {
      expect(submit.attributes('disabled')).toEqual('disabled')
    }
    expectSubmitIsDisabled()

    // begin filling in the form; check at every submit button is disabled
    wrapper.find('input#clins-0-number').setValue('0001')
    expectSubmitIsDisabled()
    wrapper.find('input#clins-0-obligated_amount').setValue('50000')
    expectSubmitIsDisabled()
    wrapper.find('input#clins-0-total_amount').setValue('60000')
    expectSubmitIsDisabled()
    wrapper.findAll('input[name="date-month"]').setValue('12')
    expectSubmitIsDisabled()
    wrapper.findAll('input[name="date-day"]').setValue('01')
    expectSubmitIsDisabled()
    wrapper.findAll('input[name="date-year"]').at(0).setValue('2020')
    expectSubmitIsDisabled()
    wrapper.findAll('input[name="date-year"]').at(1).setValue('2021')
    expectSubmitIsDisabled()
    // need to trigger the change function on the hidden date inputs so that
    // the corresponding event fires to notify the parent form that it is valid
    wrapper.find('input[name="clins-0-start_date"]').trigger('change')
    wrapper.find('input[name="clins-0-end_date"]').trigger('change')

    // check save button is enabled
    expect(submit.attributes('disabled')).toBeUndefined()
  })
})
