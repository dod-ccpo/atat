import { mount } from '@vue/test-utils'

import uploadinput from '../upload_input'
import { MockUploader } from '../../lib/upload'

import { makeTestWrapper } from '../../test_utils/component_test_helpers'

const UploadWrapper = makeTestWrapper({
  components: { uploadinput },
  templatePath: 'upload_input_template.html',
  data: function () {
    const { filename, objectName } = this.initialData
    return { filename, objectName }
  },
})

const UploadErrorWrapper = makeTestWrapper({
  components: { uploadinput },
  templatePath: 'upload_input_error_template.html',
  data: function () {
    return { filename: null, objectName: null }
  },
})

describe('UploadInput Test', () => {
  it('should show input and button when no attachment present', () => {
    const wrapper = mount(UploadWrapper, {
      propsData: {
        initialData: {},
      },
    })

    const fileInput = wrapper.find('input[type=file]').element
    expect(fileInput).not.toBe(undefined)
  })

  it('should show file name and hide input', () => {
    const wrapper = mount(UploadWrapper, {
      propsData: {
        initialData: {
          filename: 'somepdf.pdf',
          objectName: 'abcd',
        },
      },
    })

    const fileInput = wrapper.find('input[type=file]').element
    const fileNameLink = wrapper.find('.uploaded-file__name')

    expect(fileInput).toBe(undefined)
    expect(fileNameLink.html()).toContain('somepdf.pdf')
  })

  it('should correctly display error treatment', () => {
    const wrapper = mount(UploadErrorWrapper, {
      propsData: {
        initialData: { initialvalue: 'somepdf.pdf', objectName: 'abcd' },
      },
    })

    const messageArea = wrapper.find('.usa-input__message')
    expect(messageArea.html()).toContain('Test Error Message')
  })

  it('should enable the file input when the attachment is removed', () => {
    const wrapper = mount(UploadErrorWrapper, {
      propsData: {
        initialData: { filename: 'filename.pdf', objectName: 'abcd' },
      },
    })

    const event = { preventDefault: () => {}, target: { value: 'val' } }
    const component = wrapper.findComponent(uploadinput)

    component.vm.removeAttachment(event)

    expect(component.vm.$refs.attachmentInput.disabled).toBe(false)
  })
})
