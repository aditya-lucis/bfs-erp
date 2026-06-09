<template>
  <div class="fixed inset-0 z-[60] flex items-start justify-center bg-black/50 overflow-y-auto py-8">
    <div class="bg-white rounded-xl shadow-2xl w-full max-w-lg mx-4">
      <div class="bg-bfs-navy text-white px-5 py-3 rounded-t-xl flex justify-between">
        <span class="text-sm font-semibold">{{ isEdit ? 'Edit Contact' : 'Add Contact' }}</span>
        <button @click="$emit('close')" class="text-white/80">✕</button>
      </div>

      <div class="p-5 grid grid-cols-2 gap-4">
        <div>
          <label class="form-label">First Name <span class="text-red-500">*</span></label>
          <input v-model="form.first_name" class="form-input" />
        </div>
        <div>
          <label class="form-label">Middle Name</label>
          <input v-model="form.middle_name" class="form-input" />
        </div>
        <div>
          <label class="form-label">Last Name</label>
          <input v-model="form.last_name" class="form-input" />
        </div>
        <div>
          <label class="form-label">Nickname</label>
          <input v-model="form.nickname" class="form-input" />
        </div>
        <div>
          <label class="form-label">Title</label>
          <select v-model="form.title" class="form-input">
            <option value="">—</option>
            <option value="mr">Mr</option>
            <option value="mrs">Mrs</option>
            <option value="ms">Ms</option>
            <option value="dr">Dr</option>
          </select>
        </div>
        <div>
          <label class="form-label">Job Title <span class="text-red-500">*</span></label>
          <input v-model="form.job_title" class="form-input" />
        </div>
        <div>
          <label class="form-label">Gender</label>
          <select v-model="form.gender" class="form-input">
            <option value="">—</option>
            <option value="male">Male</option>
            <option value="female">Female</option>
          </select>
        </div>
        <div>
          <label class="form-label">Birthday</label>
          <input v-model="form.birthday" type="date" class="form-input" />
        </div>
        <div class="col-span-2">
          <label class="form-label">Email</label>
          <input v-model="form.email" type="email" class="form-input" />
        </div>
        <div>
          <label class="form-label">Country</label>
          <input v-model="form.country" class="form-input" />
        </div>
        <div>
          <label class="form-label">City</label>
          <input v-model="form.city" class="form-input" />
        </div>
        <div>
          <label class="form-label">Area</label>
          <select v-model="form.area" class="form-input">
            <option value="other">O - Other</option>
            <option value="jakarta">Jakarta</option>
            <option value="bandung">Bandung</option>
            <option value="surabaya">Surabaya</option>
          </select>
        </div>
        <div>
          <label class="form-label">Phone <span class="text-red-500">*</span></label>
          <input v-model="form.phone" class="form-input" />
        </div>
        <div class="col-span-2">
          <label class="form-label">Home Address</label>
          <textarea v-model="form.home_address" rows="2" class="form-input" />
        </div>
        <div>
          <label class="form-label">Mobile Phone</label>
          <input v-model="form.mobile_phone" class="form-input" />
        </div>
        <div>
          <label class="form-label">Fax</label>
          <input v-model="form.fax" class="form-input" />
        </div>
        <div class="col-span-2">
          <label class="form-label">Notes</label>
          <textarea v-model="form.notes" rows="2" class="form-input" />
        </div>
      </div>

      <div class="px-5 py-4 border-t flex justify-end gap-2 bg-gray-50 rounded-b-xl">
        <button @click="$emit('close')" class="btn-secondary text-sm">Cancel</button>
        <button @click="handleSave" class="btn-primary text-sm">{{ isEdit ? 'Update' : 'Save' }}</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({ contact: { type: Object, default: null } })
const emit = defineEmits(['close', 'save'])

const isEdit = computed(() => !!props.contact?.id)

const defaultForm = () => ({
  first_name: '', middle_name: '', last_name: '', nickname: '',
  title: '', job_title: '', gender: '', spouse: '', birthday: null,
  email: '', country: 'Indonesia', city: '', area: 'other',
  home_address: '', zip_code: '', phone: '', mobile_phone: '', fax: '', notes: '',
})

const form = ref(defaultForm())

watch(() => props.contact, (c) => {
  form.value = c ? { ...defaultForm(), ...c } : defaultForm()
}, { immediate: true })

function handleSave() {
  if (!form.value.first_name.trim()) return alert('First name wajib diisi.')
  if (!form.value.job_title.trim()) return alert('Job title wajib diisi.')
  if (!form.value.phone.trim()) return alert('Phone wajib diisi.')
  const payload = { ...form.value }
  if (!payload.birthday) payload.birthday = null
  if (props.contact?.id) payload.id = props.contact.id
  emit('save', payload)
}
</script>

<style scoped>
@reference "../../style.css";
.form-label { @apply block text-sm font-medium text-gray-700 mb-1; }
.form-input { @apply w-full border border-gray-300 rounded-lg px-3 py-1.5 text-sm; }
.btn-primary { @apply px-4 py-2 bg-bfs-gold text-white rounded-lg text-sm; }
.btn-secondary { @apply px-4 py-2 border border-gray-300 rounded-lg text-sm; }
</style>
