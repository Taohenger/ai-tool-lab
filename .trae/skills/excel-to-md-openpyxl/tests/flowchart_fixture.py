"""Designer-style DrawingML fixture: nested shapes and explicit connector endpoints."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import openpyxl

X='http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing'
A='http://schemas.openxmlformats.org/drawingml/2006/main'

def workbook(path: Path, dangling=False, smartart=False, hidden_drawing=False):
    w=openpyxl.Workbook();w.active.title='流程图';w.active['A1']='功能流程';w.active['K30']='结束';w.create_sheet('隐藏说明').sheet_state='hidden';w['隐藏说明']['A1']='隐藏内容';w.save(path)
    def shape(i,text,x,y,geo='rect',width=1800000,height=700000):
        return f'''<xdr:sp><xdr:nvSpPr><xdr:cNvPr id="{i}" name="节点{i}"/><xdr:cNvSpPr/></xdr:nvSpPr><xdr:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{width}" cy="{height}"/></a:xfrm><a:prstGeom prst="{geo}"><a:avLst/></a:prstGeom><a:solidFill><a:srgbClr val="DDEEFF"/></a:solidFill><a:ln><a:solidFill><a:srgbClr val="4472C4"/></a:solidFill></a:ln></xdr:spPr><xdr:txBody><a:bodyPr/><a:lstStyle/><a:p><a:r><a:rPr lang="zh-CN" sz="1400"/><a:t>{text}</a:t></a:r></a:p></xdr:txBody></xdr:sp>'''
    def connector(i,start,end,x,y,w,h,head=False,flip=False):
        arrow='headEnd' if head else 'tailEnd'
        transform=' flipH="1"' if flip else ''
        return f'''<xdr:cxnSp><xdr:nvCxnSpPr><xdr:cNvPr id="{i}" name="箭头{i}"/><xdr:cNvCxnSpPr><a:stCxn id="{start}" idx="2"/><a:endCxn id="{end}" idx="0"/></xdr:cNvCxnSpPr></xdr:nvCxnSpPr><xdr:spPr><a:xfrm{transform}><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm><a:prstGeom prst="straightConnector1"><a:avLst/></a:prstGeom><a:ln w="25400"><a:solidFill><a:srgbClr val="FF0000"/></a:solidFill><a:{arrow} type="triangle"/></a:ln></xdr:spPr></xdr:cxnSp>'''
    drawing=f'''<xdr:wsDr xmlns:xdr="{X}" xmlns:a="{A}"><xdr:absoluteAnchor><xdr:pos x="0" y="0"/><xdr:ext cx="6500000" cy="6000000"/><xdr:grpSp><xdr:nvGrpSpPr><xdr:cNvPr id="10" name="功能流程组合"/><xdr:cNvGrpSpPr/></xdr:nvGrpSpPr><xdr:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="6500000" cy="6000000"/><a:chOff x="0" y="0"/><a:chExt cx="6500000" cy="6000000"/></a:xfrm></xdr:grpSpPr>
{shape(1,'提交申请',2000000,500000)}{shape(2,'审核通过？',2000000,2000000,'diamond')}{shape(3,'通过：执行',500000,4000000)}{shape(4,'不通过：退回',4000000,4000000)}
{connector(5,1,2,2900000,1200000,0,800000)}{connector(6,2,3,1400000,2700000,1500000,1300000,flip=True)}{connector(7,2,999 if dangling else 4,2900000,2700000,2000000,1300000)}{connector(8,1,2,2100000,1200000,0,800000,head=True)}
</xdr:grpSp><xdr:clientData/></xdr:absoluteAnchor></xdr:wsDr>'''
    if smartart:
        drawing=drawing.replace('</xdr:wsDr>','<xdr:absoluteAnchor><xdr:pos x="0" y="0"/><xdr:ext cx="1" cy="1"/><xdr:graphicFrame/><xdr:clientData/></xdr:absoluteAnchor></xdr:wsDr>')
    with ZipFile(path) as z: data={n:z.read(n) for n in z.namelist()}
    data['xl/worksheets/sheet1.xml']=data['xl/worksheets/sheet1.xml'].replace(b'</worksheet>',b'<drawing xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" r:id="rIdFlow"/></worksheet>')
    data['xl/worksheets/_rels/sheet1.xml.rels']=b'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rIdFlow" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/drawing" Target="../drawings/drawing1.xml"/></Relationships>'
    data['xl/drawings/drawing1.xml']=drawing.encode()
    data['[Content_Types].xml']=data['[Content_Types].xml'].replace(b'</Types>',b'<Override PartName="/xl/drawings/drawing1.xml" ContentType="application/vnd.openxmlformats-officedocument.drawing+xml"/></Types>')
    if hidden_drawing:
        data['xl/worksheets/sheet2.xml']=data['xl/worksheets/sheet2.xml'].replace(b'</worksheet>',b'<drawing xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" r:id="rIdFlow"/></worksheet>')
        data['xl/worksheets/_rels/sheet2.xml.rels']=data['xl/worksheets/_rels/sheet1.xml.rels'].replace(b'drawing1.xml',b'drawing2.xml')
        data['xl/drawings/drawing2.xml']=drawing.replace('提交申请','HIDDEN_FLOW').encode()
        data['[Content_Types].xml']=data['[Content_Types].xml'].replace(b'</Types>',b'<Override PartName="/xl/drawings/drawing2.xml" ContentType="application/vnd.openxmlformats-officedocument.drawing+xml"/></Types>')
    with ZipFile(path,'w',ZIP_DEFLATED) as z:
        for n,v in data.items():z.writestr(n,v)
