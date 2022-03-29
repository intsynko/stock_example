<script>
import { defineComponent, ref } from 'vue'
import { Chart, Grid, Line } from 'vue3-charts'
import axios from "axios";

export default defineComponent({
  name: 'LineChart',
  components: { Chart, Grid, Line },
  data(){
    return {
      data: [],
      direction: 'horizontal',
      margin: {
        left: 0,
        top: 20,
        right: 20,
        bottom: 0
      }
    }
  },
  methods: {
    async get_updates(){
      return (await axios.get('http://127.0.0.1:5000/?range=50', {'Origin': 'http://127,0,0.1:3000'})).data
    },
    set_updates(data){
      this.data = {
        'ticker_00': data['ticker_00'].map((value, index) => ({'name': index, 'value': value})),
        'ticker_01': data['ticker_01'].map((value, index) => ({'name': index, 'value': value}))
      }
    },
  },
  async mounted() {
    window.setInterval(async () => {
      let data = await this.get_updates();
      this.set_updates(data);
    }, 1000);
  }
})
</script>

<template>
  <Chart
      v-for="char in data"
      :size="{ width: 500, height: 400 }"
      :data="char"
      :margin="margin"
      :direction="direction">

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
</template>

<style>
#app {
  color: black;
}
</style>