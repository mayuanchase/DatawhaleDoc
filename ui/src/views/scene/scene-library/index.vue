<template>
  <LayoutContainer header="印象图书">
    <div class="form-container">
      <el-form :model="form" label-width="120px" label-position="top" class="el-form-custom">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="语言">
              <el-select v-model="form.language" placeholder="请选择">
                <el-option label="中文" value="chinese"></el-option>
                <el-option label="英文" value="english"></el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="作者名称">
              <el-input v-model="form.author" placeholder="请输入作者名称"></el-input>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="书籍名称">
              <el-input v-model="form.bookName" placeholder="请输入书籍名称"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="印象信息">
              <el-input v-model="form.desc" placeholder="请输入你印象中的信息"></el-input>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item>
          <el-button type="primary" @click="handleSubmit">查询</el-button>
        </el-form-item>
      </el-form>

      <el-form-item label="返回文本">
        <el-input type="textarea" :value="richText" rows="10" readonly></el-input>
      </el-form-item>

      <el-loading :fullscreen="true" v-if="loading">正在回复中...</el-loading>
    </div>
  </LayoutContainer>
</template>

<script>
import applicationApi from "@/api/application";
import LayoutContainer from "@/components/layout-container/index.vue";

export default {
  components: {LayoutContainer},
  data() {
    return {
      form: {
        language: '',
        author: '',
        bookName: '',
        desc: ''
      },
      prompt: '',
      richText: '',
      libraryId: '',
      openId: '',
      loading: false
    };
  },
  created() {
    this.getLibraryIdFromUrl();
    this.getOpenId();
  },
  methods: {
    handleSubmit() {
      this.generatePrompt();
      this.fetchData();
    },
    generatePrompt() {
      let prompt = '你好，我现在想通过我的一些印象信息找书，我只能给你提供一些描述性的信息，';

      if (this.form.author) {
        prompt += `我记得图书作者为${this.form.author}，`;
      }

      if (this.form.bookName) {
        prompt += `我记得书籍名称为${this.form.bookName}，`;
      }

      if (this.form.language) {
        let language = this.form.language === 'chinese' ? '中文' : '英文';
        prompt += `我记得书籍语言是${language}，`;
      }

      if (this.form.desc) {
        prompt += `我记得书籍的内容大概是${this.form.desc}，`;
      }

      prompt += '只有这些相关信息了，帮忙查询一下，推荐几本符合条件的书的信息给我，书籍信息要包含书名，作者，出版社、存放地址，批次号';
      this.prompt = prompt;
    },
    getLibraryIdFromUrl() {
      const path = window.location.pathname;
      const regex = /\/library\/([^/]+)/;
      const match = path.match(regex);
      if (match && match[1]) {
        this.libraryId = match[1];
      } else {
        console.error('URL 中未找到 library 后面的字符串');
      }
    },
    getOpenId() {
      if (this.libraryId) {
        return applicationApi
            .getChatOpen(this.libraryId)
            .then((res) => {
              this.openId = res.data;
            });
      }
    },
    async fetchData() {
      this.loading = true;
      this.richText = ''; // 清空之前的内容
      const obj = {
        message: this.prompt,
        re_chat: false
      };

      try {
        const response = await applicationApi.postChatMessage(this.openId, obj);
        if (response.status === 401) {
          application.asyncAppAuthentication(accessToken).then(() => {
            chatMessage(chat);
          }).catch((err) => {
            errorWrite(chat);
          });
        } else if (response.status === 460) {
          this.$message.error('无法识别用户身份');
        } else if (response.status === 461) {
          this.$message.error('抱歉，您的提问已达到最大限制，请明天再来吧！');
        } else {
          const reader = response.body.getReader();
          const decoder = new TextDecoder('utf-8');

          let receivedText = '';

          const readStream = () => {
            reader.read().then(({done, value}) => {
              if (done) {
                this.loading = false;
                const lines = receivedText.split('\n');
                let contentArray = [];
                lines.forEach((line) => {
                  try {
                    if (line) {
                      const jsonStr = line.trim().replace('data: ', '');
                      const json = JSON.parse(jsonStr);
                      if (json && json.content) {
                        contentArray.push(json.content);
                      }
                    }
                  } catch (error) {
                    console.error('解析 JSON 出错:', error);
                  }
                });
                this.richText = contentArray.join('');
              } else {
                if (value) {
                  receivedText += decoder.decode(value, {stream: true});
                  const lines = receivedText.split('\n');
                  let contentArray = [];
                  lines.forEach((line) => {
                    try {
                      if (line) {
                        const jsonStr = line.trim().replace('data: ', '');
                        const json = JSON.parse(jsonStr);
                        if (json && json.content) {
                          contentArray.push(json.content);
                        }
                      }
                    } catch (error) {
                      console.error('解析 JSON 出错:', error);
                    }
                  });
                  this.richText = contentArray.join('');
                  readStream();
                }

              }
            });
          };

          readStream();
        }
      } catch (error) {
        this.loading = false;
        this.$message.error('请求出错，请稍后重试');
      }
    }
  }
};
</script>

<style>
.form-container {
  padding: 20px;
  background-color: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.el-form-custom .el-form-item {
  margin-bottom: 20px;
}

.prompt {
  margin-top: 20px;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 5px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
</style>
