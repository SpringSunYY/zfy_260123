<template>
  <div>{{ id }}{{ modelInfo}}</div>
</template>
<script>
import {getRecommend} from "@/api/car/recommend";

export default {
  name: "index",
  components: {},
  data() {
    return {
      id: null,
      modelInfo: {}
    }
  },
  created() {
    this.id = this.$route.params.id;
    if (this.id) {
      this.getRecommendModel();
    }
  },
  methods: {
    getRecommendModel() {
      getRecommend(this.id).then(response => {
        if (!response.data.modelInfo) {
          return
        }
        this.modelInfo = response.data.modelInfo;
      });
    }
  }
}
</script>
<style scoped lang="scss">

</style>
