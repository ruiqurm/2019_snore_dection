
Page
({
  data:
  {
    list:[],
    name:''
  },
onLoad:function(options)
{
  var that = this;
  var id;
  wx.request({
    url: 'http://39.105.60.226/api/audio',
    method:'get',
    success: function (res) {
      let data1 = res.data.file;
      console.log(res.data)
      console.log(data1[0].full_name)
      that.setData
        ({
          list: data1,
          name: data1[0].full_name
        })
       // console.log(that.data.list)
    },
 })
 
 
 
},
download:function()
{
  var url = 'http://39.105.60.226/api/audio/' + this.data.name.slice(0, -4);
  console.log(url)
  wx.downloadFile({
    url: url,
    success:function(res)
    {
      console.log('s')
          wx.playVoice({
            filePath: res.tempFilePath,
       })
    }
  })
}
})