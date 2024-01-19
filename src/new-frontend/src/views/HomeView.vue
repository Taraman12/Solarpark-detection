<script setup>
import { mdiSatelliteVariant, mdiGithub } from '@mdi/js'
import SectionMain from '@/components/SectionMain.vue'
import CardBox from '@/components/CardBox.vue'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import SectionTitle from '@/components/SectionTitle.vue'
import BaseButton from '@/components/BaseButton.vue'
import BaseDivider from '@/components/BaseDivider.vue'
</script>

<template>
  <LayoutAuthenticated>
    <SectionMain>

      <SectionTitleLineWithButton :icon="mdiSatelliteVariant" title="Continues Solar Park Detection" main>
        <BaseButton href="https://github.com/Taraman12/Solarpark-detection" target="_blank" :icon="mdiGithub"
          label="Star on GitHub" color="contrast" rounded-full small />
      </SectionTitleLineWithButton>
      <p class="text-xl">
        This project uses a self trained neural network to detect solar parks from satellite images.<br>
        Used key technologies:
      <ul class="list-disc ml-10">
        <li> <i>PyTorch</i> for model development and <b>TorchServe</b> for model serving</li>
        <li> FastAPI for the backend and Postgres for DB</li>
        <li> Vue.js for the frontend and NGINX for reverse proxy</li>
        <li> Docker for containerization and Docker Swarm for orchestration</li>
      </ul>

      </p>
      <SectionTitle :first=false>
        Pipeline
      </SectionTitle>
      <CardBox>
        <img src="../assets/pipeline_ec2.svg" alt="pipeline" />
      </CardBox>
      <SectionTitle :first=false>
        Comparison backbones of the ML-Model
      </SectionTitle>
      <CardBox has-table>
      <table>
        <thead>
          <tr>
            <th>Model</th>
            <th>Max. Dice (%)</th>
            <th>Mean Dice (%)</th>
            <th>Mean F1 (%)</th>
            <th>Mean Precision (%)</th>
            <th>Mean Recall (%)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>EfficientNet-B0</td>
            <td>69.86</td>
            <td>59.25</td>
            <td>58.39</td>
            <td>70.93</td>
            <td>57.48</td>
          </tr>
          <tr>
            <td>ResNet18</td>
            <td>71.07</td>
            <td>59.68</td>
            <td>58.82</td>
            <td>69.20</td>
            <td>55.07</td>
          </tr>
          <tr>
            <td>ResNeSt14d</td>
            <td>76.67</td>
            <td>71.16</td>
            <td>70.34</td>
            <td>76.15</td>
            <td>69.63</td>
          </tr>
          <tr>
            <td>VGG11</td>
            <td>75.25</td>
            <td>61.94</td>
            <td>61.25</td>
            <td>68.67</td>
            <td>59.46</td>
          </tr>
        </tbody>
      </table>
    </CardBox>
    </SectionMain>
  </LayoutAuthenticated>
</template>
