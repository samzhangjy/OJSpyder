<template>
  <div class="hello container">
    <div v-if="!loaded">
      <h1>查看题目</h1>
      <p>请输入题目编号</p>
      <vs-input v-model="pid" placeholder="题目编号" autofocus autocomplete="off">
        <template v-if="!valid" #message-danger>
          请输入题目编号
        </template>
      </vs-input>
      <vs-button type="filled" @click="getProblem()">获取题目信息</vs-button>
    </div>
    <div v-if="loaded" class="container">
      <h1 class="text-center">{{ problem.pid }}. {{ problem.title }} <small>({{ problem.type }})</small></h1>
      <br>
      <h3 class="text-center">题目描述</h3>
      <p class="container">{{ problem.content }}</p>
      <br>
      <h3 class="text-center">输入</h3>
      <p class="container">{{ problem.input }}</p>
      <h3 class="text-center">输出</h3>
      <p class="container">{{ problem.output }}</p>
      <h3 class="text-center">输入样例</h3>
      <p class="container">{{ problem.sample_input }}</p>
      <h3 class="text-center">输出样例</h3>
      <p class="container">{{ problem.sample_output }}</p>
      <h3 class="text-center">数据范围限制</h3>
      <p class="container" v-if="problem.limits">{{ problem.limits }}</p>
      <p class="container" v-else>无</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Main',
  data: function () {
    return {
      pid: '',
      valid: true,
      loaded: false,
      problem: {}
    }
  },
  methods: {
    getProblem: async function () {
      if (this.pid === '') {
        this.valid = false
        return
      }
      const loading = this.$vs.loading()
      await axios.get(`http://localhost:5000/api/problems/get/${this.pid}`).then((data) => {
        this.loaded = true
        this.problem = data.data.problem
        loading.close()
      }).catch((err) => {
        loading.close()
        this.$vs.notification({
          color: 'warn',
          title: '获取失败',
          text: `无法自动获取题目信息：${err}。请检查是否启动了后台API和是否登录。`
        })
      })
    }
  }
}
</script>

<style scoped>
.text-center {
  text-align: center;
}
</style>
