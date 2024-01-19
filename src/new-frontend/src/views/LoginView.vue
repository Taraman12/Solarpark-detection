<script setup>
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { mdiAccount, mdiAsterisk } from '@mdi/js'
import { useMainStore } from '@/stores/main'
import { useFetch } from '@/plugins/fetch'
import SectionFullScreen from '@/components/SectionFullScreen.vue'
import CardBox from '@/components/CardBox.vue'
import FormCheckRadio from '@/components/FormCheckRadio.vue'
import FormField from '@/components/FormField.vue'
import FormControl from '@/components/FormControl.vue'
import BaseButton from '@/components/BaseButton.vue'
import BaseButtons from '@/components/BaseButtons.vue'
import LayoutGuest from '@/layouts/LayoutGuest.vue'

const { logInGetToken, get } = useFetch()

const mainStore = useMainStore()

const form = reactive({
  login: 'John@doe.com',
  pass: 'password',
  remember: true
})

const userForm = reactive({
  name: mainStore.userName,
  email: mainStore.userEmail,
  access_token: mainStore.access_token
})

const router = useRouter()

async function submit() {
  try {
    const response = logInGetToken(form.login, form.pass)
    const data = await response
    if (data == null) {
      console.log("API error")
      return
    }
    mainStore.setUser(userForm)
    const user = await get('user/me')
    console.log("user", user)
    console.log("data", data)
    userForm.name = user.full_name
    userForm.email = form.login
    userForm.access_token = data.access_token
    mainStore.setUser(userForm)
    router.push('/')
  } catch (error) {
    console.error("submit error:", error)
  }
}

const submit2 = () => {
  mainStore.setUser(userForm)
  console.log(mainStore.userName)
  console.log(mainStore.userEmail)
  console.log(mainStore.access_token)
}
</script>

<template>
  <LayoutGuest>
    <SectionFullScreen v-slot="{ cardClass }" bg="purplePink">
      <CardBox :class="cardClass" is-form @submit.prevent="submit">
        <FormField label="Login" help="Please enter your login">
          <FormControl v-model="form.login" :icon="mdiAccount" name="login" autocomplete="username" />
        </FormField>

        <FormField label="Password" help="Please enter your password">
          <FormControl v-model="form.pass" :icon="mdiAsterisk" type="password" name="password"
            autocomplete="current-password" />
        </FormField>

        <FormCheckRadio v-model="form.remember" name="remember" label="Remember" :input-value="true" />

        <template #footer>
          <BaseButtons>
            <BaseButton type="submit" color="info" label="Login" />
            <BaseButton to="/dashboard" color="info" outline label="Back" />
            <BaseButton color="info" label="Options" outline @click="submit2" />
          </BaseButtons>
        </template>
      </CardBox>
    </SectionFullScreen>
  </LayoutGuest>
</template>
