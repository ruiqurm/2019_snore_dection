Page
({
data:
{
  o:'',
  o1:'',
  o2:'',
  o3:''
},
  onLoad:function(options)
  {
    console.log(options.id)
    var o,o1,o2,o3;
    var that = this;
    var p = options.id;
    var p1 = options.id1;
    var p2 = options.id2;
    var p3 = options.id3;
    console.log(p)
    that.setData
    ({
      p:p,
      p1: p1,
      p2: p2,
      p3: p3,
    })
    o='http://39.105.60.226/api'+that.data.p;
    o1 = 'http://39.105.60.226/api' + that.data.p1;
    o2 = 'http://39.105.60.226/api' + that.data.p2;
    o3 = 'http://39.105.60.226/api' + that.data.p3;
    that.setData
    ({
      o:o,
      o1:o1,
      o2:o2,
      o3:o3
    })
    console.log(that.data.o)
  }
})