<script setup>
/* eslint-disable no-undef */
import { onMounted, onUnmounted, reactive, ref } from 'vue'
import { mdiBallotOutline, mdiAccount, mdiCloud, mdiTrashCan, mdiCalendarBlank, mdiCropSquare, mdiCreation } from '@mdi/js'
import SectionMain from '@/components/SectionMain.vue'
import CardBox from '@/components/CardBox.vue'
import FormField from '@/components/FormField.vue'
import FormControl from '@/components/FormControl.vue'
import BaseDivider from '@/components/BaseDivider.vue'
import BaseButton from '@/components/BaseButton.vue'
import BaseButtons from '@/components/BaseButtons.vue'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import { useFetch } from '@/plugins/fetch'
import { useToast } from "vue-toastification";
import NumberDynamic from '@/components/NumberDynamic.vue'

const { get, post, del } = useFetch()

const toast = useToast()

let intervalCheckInstance;
let intervalIdServiceOnline;
let intervalIdPredictionInDB;

const startInstance = reactive({
  instance_tag: 'Worker',
  instance_type: 't3.medium',
})

const runPrediction = reactive({
  service_name: 'main_processing:7000',
  start_date: '2020-05-01',
  end_date: '2020-07-02',
  model: 'solar-park-detection',
  tiles_list: ["32UNA"]
})

const modelNames = reactive({
  model: 'solar-park-detection'
})

// async function getSubmit(endpoint) {
//   try {
//     const response = get(endpoint)
//     const data = await response
//     if (response.status_code == 401) {
//       console.log("unauthorized")
//     }
//     if (data == null) {
//       console.log("API error")
//       return
//     }
//     console.log("data", data)
//   } catch (error) {
//     console.error("submit error:", error)
//   }
//   console.log(endpoint)

// }

async function postSubmit(endpoint, formData) {
  console.log(formData)
  console.log(endpoint)
  try {
    const response = post(endpoint, formData)
    const data = await response
    if (response.status_code == 401) {
      console.log("unauthorized")
    }
    if (data == null) {
      console.log("API error")
      return
    }
    console.log("data", data)
  } catch (error) {
    console.error("submit error:", error)
  }
}

let ec2Instances = ref(false);
let amountOfInstances = ref(0);
let serviceOnline = ref(false);
let serviceCheck = ref(false);

let predictionInDB = ref(0);

async function checkInstance() {
  const response = get("instance/running-instances")
  const ec2Instances = await response
  console.log("ec2Instances", ec2Instances)
  if (ec2Instances.errors === undefined) {
    console.log("Instance is currently running")
    amountOfInstances.value = Object.keys(ec2Instances).length
    return ec2Instances
  }
  else {
    console.log("No instance is currently running")
    return false
  }
}

// const listServiceFunc = async () => {
//   const response = get("service/list-services")
//   const data = await response
//   if (response.status_code == 401) {
//     console.log("unauthorized")
//   }
//   if (data == null) {
//     console.log("API error")
//     return
//   }
//   console.log("data", data)
// }

const terminateInstance = async (instanceId) => {
  // const listServiceGet = get("service/list-services")
  // const listService = await listServiceGet
  // console.log("listService", listService)
  del("service/remove-service/main_processing")
  del("service/remove-service/main_ml-serve")
  const response = del(`instance/terminate/${instanceId}`)
  const data = await response
  console.log("data del", data)
  if (response.status_code == 401 || response.status_code == 403) {
    console.log("unauthorized")
    toast.error("Not logged in", { timeout: 1500 })
    return
  }
  if (data == null) {
    console.log("API error")
    return
  }
  toast.success("Instance terminated", { timeout: 1500 })
}

const CheckService = async (service_name) => {
  const service = { service_name: service_name }
  const response = get("service/run-service-checks", service)
  const data = await response
  if (data.Message === 'All checks passed') {
    console.log('All checks passed');
    serviceCheck.value = true
    return true
  } else {
    console.log('Some checks did not pass');
    return false
  }
}

const testServiceOnline = async () => {
  const service = { service_name: "processing:7000" }
  const response = get("service/test-connection-service", service)
  const data = await response
  if (data == null) {
    console.log("API error")
    return false
  }

  if (Object.keys(data)[0] == "error") {
    console.log("API error")
    return false
  }
  console.log("data", data)
  serviceCheck.value = CheckService("main_processing:7000")
  return true
}

const startPrediction = async () => {
  const params = { service_name: runPrediction.service_name, start_date: runPrediction.start_date, end_date: runPrediction.end_date }
  // const payload = { runPrediction.tiles_list }
  const response = post("service/run-prediction", params, runPrediction.tiles_list)
  const data = await response
  console.log("data startPrediction.status", data.ok)
  if (data == null) {
    console.log("API error")
    return false
  }
  if (data.ok) {
    console.log("Prediction started")
    toast.success("Prediction started", { timeout: 1500 })
    return true
  }
  else {
    console.log("Prediction failed")
    toast.error("Prediction failed", { timeout: 1500 })
    return false
  }
}

const getPredictionsInDB = async () => {
  const response = get("prediction")
  const data = await response
  if (data == null) {
    console.log("API error")
    return false
  }
  return data.length
}

let models = ref(false);

const getModels = async () => {
  const response = get("models")
  const data = await response
  console.log("data models", data[0])
  if (data == null) {
    console.log("API error")
    return false
  }
  return data
}
// const setIntervalCheckInstance = () => {
//   intervalCheckInstance = setInterval(async () => {
//     ec2Instances.value = await checkInstance();
//     console.log("ec2Instances", ec2Instances.value)
//   }, 3000);
// }

// const setIntervalCheckServiceOnline = () => {
//   intervalIdServiceOnline = setInterval(async () => {
//     serviceOnline.value = await testServiceOnline();
//     console.log("serviceOnline", serviceOnline.value)
//   }, 3000);
// }

onMounted(async () => {
  ec2Instances.value = await checkInstance()
  serviceOnline.value = await testServiceOnline()
  predictionInDB.value = await getPredictionsInDB()
  models.value = await getModels()
  intervalCheckInstance = setInterval(async () => {
    ec2Instances.value = await checkInstance();
    console.log("ec2Instances", ec2Instances.value)
  }, 3000);
  intervalIdServiceOnline = setInterval(async () => {
    serviceOnline.value = await testServiceOnline();
    console.log("serviceOnline", serviceOnline.value)
  }, 3000);
  intervalIdPredictionInDB = setInterval(async () => {
    predictionInDB.value = await getPredictionsInDB();
    console.log("serviceOnline", serviceOnline.value)
  }, 3000);
});


onUnmounted(() => {
  clearInterval(intervalCheckInstance)
  clearInterval(intervalIdServiceOnline)
  clearInterval(intervalIdPredictionInDB)
})
</script>

<template>
  <LayoutAuthenticated>
    <SectionMain>
      <SectionTitleLineWithButton :icon="mdiBallotOutline" title="Start model" main>
      </SectionTitleLineWithButton>
      <CardBox class="mb-6" has-table>
        <Transition>
          <div v-if="!ec2Instances">
            <div class="text-center">
              <div role="status">
                <!-- <svg aria-hidden="true" class="inline w-8 h-8 text-gray-200 animate-spin dark:text-gray-600 fill-blue-600"
                  viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path
                    d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z"
                    fill="currentColor" />
                  <path
                    d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z"
                    fill="currentFill" />
                </svg> -->
                <span class="text-xl leading-tight font-semibold animate-pulse">Loading running instances...</span>
              </div>
            </div>
          </div>
          <div v-else>
            <table>
              <thead>
                <tr>
                  <th>Instance ID</th>
                  <th>Service</th>
                  <th>Instance type</th>
                  <th>Instance state</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                <tr v-for="(ec2Instance, instanceId) in ec2Instances" :key="instanceId">
                  <td>{{ instanceId }}</td>
                  <td data-label="Service">{{ ec2Instance.Tag }}</td>
                  <td data-label="Instance Type">{{ ec2Instance.Type }}</td>
                  <td>{{ ec2Instance.State }}</td>

                  <td class="before:hidden lg:w-1 whitespace-nowrap">
                    <div v-if="ec2Instance.Tag != 'manager-instance'">
                      <BaseButtons type="justify-start lg:justify-end" no-wrap>
                        <BaseButton color="danger" :icon="mdiTrashCan" small @click="terminateInstance(instanceId)" />
                      </BaseButtons>
                    </div>
                  </td>

                </tr>
              </tbody>
            </table>
          </div>
        </Transition>
      </CardBox>
      <BaseDivider />
      <CardBox start-instance @submit.prevent="postSubmit(endpoint, startInstance)">
        <FormField label="Start ec2 instances">
          <FormControl v-model="startInstance.instance_tag" placeholder="Service Name" :icon="mdiAccount" />
          <FormControl v-model="startInstance.instance_type" placeholder="EC2 instance type" :icon="mdiCloud" />
        </FormField>
        <template #footer>
          <BaseButtons>
            <BaseButton type="postSubmit" color="info" label="Start instance"
              @click="postSubmit('service/start-service', startInstance)" />
          </BaseButtons>
        </template>
      </CardBox>
      <BaseDivider />
      <CardBox>
        <div>
          <h3 class="text-lg leading-tight text-gray-500 dark:text-slate-400">
            Predictions in DB
          </h3>
          <!-- https://vuejs.org/guide/extras/animation.html#animating-with-watchers -->
          <h1 class="text-3xl leading-tight font-semibold">
            <NumberDynamic :value="predictionInDB" />
          </h1>
        </div>
      </CardBox>
      <BaseDivider />
      <Transition>
        <div v-if="amountOfInstances < 2" class="text-center text-xl leading-tight font-semibold">
          Start instance first to run predictions
        </div>
        <div v-else-if="!serviceOnline" class="text-center text-xl leading-tight font-semibold">
          Waiting for service to be online
        </div>
        <div v-else-if="!serviceCheck" class="text-center text-xl leading-tight font-semibold">
          Waiting for service to pass checks
        </div>
        <div v-else>
          <CardBox run-prediction @submit.prevent="startPrediction()">
            <FormField label="Start predictions on tiles with date">
              <FormControl v-model="runPrediction.service_name" placeholder="Service name with port" :icon="mdiCloud" />
              <FormControl v-model="runPrediction.tiles_list" placeholder="Tiles list" :icon="mdiCropSquare" />

              <FormControl v-model="runPrediction.start_date" placeholder="Start date" :icon="mdiCalendarBlank" />
              <FormControl v-model="runPrediction.end_date" placeholder="End date" :icon="mdiCalendarBlank" />
              <FormControl v-model="runPrediction.model" placeholder="Model name" :icon="mdiCreation" />
            </FormField>

            <template #footer>
              <BaseButtons>
                <BaseButton type="postSubmit" color="info" label="Run prediction" @click="startPrediction()" />
              </BaseButtons>
            </template>
          </CardBox>
        </div>
      </Transition>

      <BaseDivider />

      <SectionTitleLineWithButton :icon="mdiCreation" title="Change model" main>
      </SectionTitleLineWithButton>
      <div class="text-xl leading-tight font-semibold m-2">
        <h3>Currently Registered Models</h3>
      </div>
      <CardBox has-table>
        <table class="table-auto">
          <thead>
            <tr>
              <th>Model name</th>
              <th>Model url</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="model in models" :key="Object.keys(model)">
              <td>{{ model.modelName }}</td>
              <td>{{ model.modelUrl }}</td>
            </tr>
          </tbody>
        </table>
      </CardBox>
      <BaseDivider />
      <CardBox model-names @submit.prevent="postSubmit()">
        <FormField label="Register Model from solar-park-detection S3 Bucket">
          <FormControl v-model="modelNames.model" placeholder="Model name" :icon="mdiCreation" />
        </FormField>

        <template #footer>
          <BaseButtons>
            <BaseButton type="postSubmit" color="info" label="Register Model"
              @click="post(`models/${modelNames.model}`)" />
            <BaseButton type="postSubmit" color="danger" label="Unregister Model"
              @click="del(`models/${modelNames.model}`)" />
          </BaseButtons>
        </template>
      </CardBox>
    </SectionMain>
  </LayoutAuthenticated>
</template>
<style>
.v-enter-active,
.v-leave-active {
  transition: opacity 0.3s ease;
}

.v-enter-from,
.v-leave-to {
  opacity: 0;
}
</style>
