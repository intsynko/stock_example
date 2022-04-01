<script>
import { defineComponent, ref } from 'vue'
import { Chart, Grid, Line } from 'vue3-charts'
import axios from "axios";


const server = import.meta.env.VUE_APP_SERVER_ADRESS || 'http://127.0.0.1:5000'

console.log("process");
console.log(import.meta);

const ORIGIN = {
  'Access-Control-Allow-Origin': 'http://127.0.0.1:3000',
  'Access-Control-Allow-Credentials': 'true',
}

export default defineComponent({
  name: 'LineChart',
  components: { Chart, Grid, Line },
  data(){
    return {
      chart_data: [],
      updates_enables: true,
      sleep_delay: 1,
      range_cnt: 5,
      range_type: 's',
      last_minute_show: 1,
      labels:[],
      label: null,
      alert_label: null,
    }
  },
  methods: {
    async sleep(seconds){
      await new Promise(r => setTimeout(r, seconds * 1000));
    },
    async update_chart() {
      let data = null;
      try {
        data = await this.get_updates(this.label, this.range_cnt, this.range_type, this.last_minute_show);
      } catch (e) {
        this.alert_label = "Временно недоступен сервер";
      }
      this.alert_label = null;
      if (data!==null)
        this.set_updates(data);
    },
    async get_updates(label, range_cnt, range_type, last_minute_show){
      return (await axios.get(`${server}/ticker/${label}?range_cnt=${range_cnt}&range_type=${range_type}&last_minute_show=${last_minute_show}`, ORIGIN)).data
    },
    async get_labels(){
      return (await axios.get(`${server}/ticker/`, ORIGIN)).data
    },
    set_updates(data){
      this.chart_data = data
    },
    async auto_update(){
      while (true){
          if (this.updates_enables && this.label !== null){
            this.update_chart();
          }
          await this.sleep(this.sleep_delay);
      }
    }
  },
  watch: {
    label: async function (){
      await this.update_chart();
    },
  },
  async mounted() {
    try {
      this.labels = await this.get_labels();
    } catch (e) {
      this.alert_label = "Временно недоступен сервер";
      // await this.sleep(1);
      // this.alert_label = null;
    }
    this.auto_update();
  }
})
</script>

<template>
  <div>
    <b-card
        tag="article"
        style="width: 1200px;"
        class="mb-2"
    >
      <b-card-header>
        Инструмент
        <b-dropdown
            :text="this.label || 'Выберите инструмент'"
        >
          <b-dropdown-item
              v-for="item in this.labels"
              :key="item"
              :value="item"
              @click="this.label = item"
          >
            {{item}}
          </b-dropdown-item>
        </b-dropdown>
        , обновлять раз в
        <b-dropdown
            :text="this.updates_enables? this.sleep_delay: 'никогда'"
        >
          <b-dropdown-item :key="-1" :value="'не обновлять'" @click="this.updates_enables = false">не обновлять</b-dropdown-item>
          <b-dropdown-item
              v-for="item in [1, 2, 3, 5, 10]"
              :key="item"
              :value="item"
              @click="this.updates_enables = true; this.sleep_delay = item"
          >
            {{item}}
          </b-dropdown-item>
        </b-dropdown>
        секунд, группировать по
        <b-dropdown
            :text="`${this.range_cnt}${this.range_type}`"
        >
          <b-dropdown-item
              v-if="last_minute_show <= 2"
              v-for="item in [1, 5, 10, 15, 30]"
              :key="item"
              :value="item"
              @click="this.range_cnt = item; this.range_type = 's'"
          >
            {{item}} сек
          </b-dropdown-item>
          <b-dropdown-item
              v-for="item in [1, 5, 10, 15, 30]"
              v-if="last_minute_show > 2"
              :key="item"
              :value="item"
              @click="this.range_cnt = item; this.range_type = 'm'"
          >
            {{item}} мин
          </b-dropdown-item>
        </b-dropdown>
        за последние
        <b-dropdown
            :text="this.last_minute_show + ' мин'"
        >
          <b-dropdown-item
              v-for="item in [1, 2, 5, 10, 15]"
              :key="item"
              :value="item"
              @click="() => {
                this.last_minute_show = item;
                if (this.last_minute_show > 2 && this.range_type === 's') {
                  this.range_type = 'm';
                  this.range_cnt = 1;
                }}"
          >
            {{item}} мин
          </b-dropdown-item>
        </b-dropdown>
      </b-card-header>
      <b-badge variant="danger">{{this.alert_label}}</b-badge>
      <Chart
          :size="{ width: 1000, height: 400 }"
          :data="chart_data"
          :margin="{left: 0, top: 20, right: 20, bottom: 0}"
          :direction="'horizontal'">

        <template #layers>
          <Grid strokeDasharray="2,2" />
          <Line :dataKeys="['name', 'value']"
                type="monotone"
                :lineStyle="{
                stroke: '#9f7aea'
              }"
          />
        </template>
      </Chart>
    </b-card>
  </div>
</template>

<style>
#app {
  color: black;
}
</style>