import Vue from 'vue'
import { mount } from '@vue/test-utils'

import PopDateRange from '../pop_date_range'

import { makeTestWrapper } from '../../test_utils/component_test_helpers'

const PopDateRangeWrapper = makeTestWrapper({
  components: { PopDateRange },
  templatePath: 'pop_date_range.html',
  data: function () {
    return {
      initialMinStartDate: '2019-09-14',
      initialMaxEndDate: '2022-09-14',
    }
  },
})

describe('PopDateRange Test', () => {
  const component = new Vue(PopDateRange)

  it('should calculate the max start date', () => {
    component.contractEnd = new Date('2020-01-01')
    const date = new Date('2019-12-31')
    expect(component.calcMaxStartDate(date)).toEqual(date)
  })

  it('should calculate the min end date', () => {
    component.contractStart = new Date('2020-01-01')
    const date = new Date('2020-02-02')
    expect(component.calcMinEndDate(date)).toEqual(date)
  })

  it('should add an error to the start date if it is out of range', () => {
    const wrapper = mount(PopDateRangeWrapper, {
      propsData: {
        initialData: {},
      },
    })

    const error = ['usa-input--error']
    var startDateField = wrapper.find('fieldset[name="start_date"]')
    var endDateField = wrapper.find('fieldset[name="end_date"]')

    // set valid date range
    startDateField.find('input[name="date-month"]').setValue('01')
    startDateField.find('input[name="date-day"]').setValue('01')
    startDateField.find('input[name="date-year"]').setValue('2020')

    endDateField.find('input[name="date-month"]').setValue('01')
    endDateField.find('input[name="date-day"]').setValue('01')
    endDateField.find('input[name="date-year"]').setValue('2021')

    // manually trigger the change event in the hidden fields
    startDateField.find('input[name="start_date"]').trigger('change')
    endDateField.find('input[name="end_date"]').trigger('change')

    // check that both dates do not have error class
    expect(startDateField.classes()).toEqual(expect.not.arrayContaining(error))
    expect(endDateField.classes()).toEqual(expect.not.arrayContaining(error))

    // update start date to be after end date and trigger change event
    startDateField.find('input[name="date-year"]').setValue('2022')
    startDateField.find('input[name="start_date"]').trigger('change')

    expect(startDateField.classes()).toEqual(expect.arrayContaining(error))
    expect(endDateField.classes()).toEqual(expect.not.arrayContaining(error))
  })

  it('should add an error to the end date if it is out of range', () => {
    const wrapper = mount(PopDateRangeWrapper, {
      propsData: {
        initialData: {},
      },
    })

    const error = ['usa-input--error']
    var startDateField = wrapper.find('fieldset[name="start_date"]')
    var endDateField = wrapper.find('fieldset[name="end_date"]')

    // set valid date range
    startDateField.find('input[name="date-month"]').setValue('01')
    startDateField.find('input[name="date-day"]').setValue('01')
    startDateField.find('input[name="date-year"]').setValue('2020')

    endDateField.find('input[name="date-month"]').setValue('01')
    endDateField.find('input[name="date-day"]').setValue('01')
    endDateField.find('input[name="date-year"]').setValue('2021')

    // manually trigger the change event in the hidden fields
    startDateField.find('input[name="start_date"]').trigger('change')
    endDateField.find('input[name="end_date"]').trigger('change')

    // check that both dates do not have error class
    expect(startDateField.classes()).toEqual(expect.not.arrayContaining(error))
    expect(endDateField.classes()).toEqual(expect.not.arrayContaining(error))

    // update end date to be before end date and trigger change event
    endDateField.find('input[name="date-year"]').setValue('2019')
    endDateField.find('input[name="end_date"]').trigger('change')

    expect(startDateField.classes()).toEqual(expect.not.arrayContaining(error))
    expect(endDateField.classes()).toEqual(expect.arrayContaining(error))
  })

  it('should add an error to the end date if it is the same as start date', () => {
    const wrapper = mount(PopDateRangeWrapper, {
      propsData: {
        initialData: {},
      },
    })

    const error = ['usa-input--error']
    var startDateField = wrapper.find('fieldset[name="start_date"]')
    var endDateField = wrapper.find('fieldset[name="end_date"]')

    // set valid date range
    startDateField.find('input[name="date-month"]').setValue('01')
    startDateField.find('input[name="date-day"]').setValue('01')
    startDateField.find('input[name="date-year"]').setValue('2020')

    endDateField.find('input[name="date-month"]').setValue('01')
    endDateField.find('input[name="date-day"]').setValue('01')
    endDateField.find('input[name="date-year"]').setValue('2020')

    // manually trigger the change event in the hidden fields
    startDateField.find('input[name="start_date"]').trigger('change')
    endDateField.find('input[name="end_date"]').trigger('change')

    // check that end date has error class
    expect(startDateField.classes()).toEqual(expect.not.arrayContaining(error))
    expect(endDateField.classes()).toEqual(expect.arrayContaining(error))
  })

  it('should add an error to the start date if it is the same as end date', () => {
    const wrapper = mount(PopDateRangeWrapper, {
      propsData: {
        initialData: {},
      },
    })

    const error = ['usa-input--error']
    var startDateField = wrapper.find('fieldset[name="start_date"]')
    var endDateField = wrapper.find('fieldset[name="end_date"]')

    // set valid date range
    startDateField.find('input[name="date-month"]').setValue('01')
    startDateField.find('input[name="date-day"]').setValue('01')
    startDateField.find('input[name="date-year"]').setValue('2020')

    endDateField.find('input[name="date-month"]').setValue('01')
    endDateField.find('input[name="date-day"]').setValue('01')
    endDateField.find('input[name="date-year"]').setValue('2020')

    // manually trigger the change event in the hidden fields
    endDateField.find('input[name="end_date"]').trigger('change')
    startDateField.find('input[name="start_date"]').trigger('change')

    // check that start date has error class
    expect(startDateField.classes()).toEqual(expect.arrayContaining(error))
    expect(endDateField.classes()).toEqual(expect.not.arrayContaining(error))
  })
})
