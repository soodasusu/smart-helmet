/**
 * 高德地图 composable — 封装 AMap 初始化、标记管理、定位
 */

import { ref } from 'vue'
import { getAlerts, createAlert, deleteAlerts } from '@/services/api'

const DEFAULT_CENTER = [118.9075, 32.1185] // 南京邮电大学仙林校区
const DEFAULT_ZOOM = 16
const LOCATION_INTERVAL = 30000

export function useAmap(containerId = 'map') {
  const map = ref(null)
  const geolocation = ref(null)
  const markers = ref([])
  const currentLocationMarker = ref(null)
  const isAddingMode = ref(false)
  const locationInterval = ref(null)

  // ── 颜色映射（按威胁等级） ──
  const markerColors = {
    high: '#dc2626',
    medium: '#f59e0b',
    low: '#eab308'
  }

  const threatText = {
    high: '高威胁',
    medium: '中威胁',
    low: '低威胁'
  }

  // ── 初始化地图 ──
  const initMap = () => {
    if (!window.AMap) {
      console.error('AMap SDK not loaded')
      return
    }

    map.value = new AMap.Map(containerId, {
      zoom: DEFAULT_ZOOM,
      center: DEFAULT_CENTER,
      resizeEnable: true
    })

    map.value.on('click', (e) => {
      if (isAddingMode.value) {
        // 外部处理添加标记
      }
    })

    return map.value
  }

  // ── 加载标记（从后端拉取人工标记） ──
  const loadMarkers = async () => {
    try {
      const { data } = await getAlerts({ source: 'manual' })
      markers.value = (data.alerts || []).map(v => ({
        id: v.id,
        lng: v.longitude,
        lat: v.latitude,
        type: v.threat_level || 'medium',
        description: v.description || '',
        time: v.created_at
      }))
    } catch {
      markers.value = []
    }
  }

  const renderMarkers = () => {
    if (!map.value) return
    markers.value.forEach((m) => {
      const marker = new AMap.Marker({
        position: [m.lng, m.lat],
        title: m.description,
        icon: createMarkerIcon(m.type)
      })
      marker.setMap(map.value)

      // 点击弹窗
      marker.on('click', () => {
        const info = new AMap.InfoWindow({
          content: `
            <div style="padding:10px;max-width:200px">
              <b>${threatText[m.type] || '中威胁'}</b>
              <p style="margin:5px 0">${m.description || '无描述'}</p>
              <small>${m.lat.toFixed(4)}, ${m.lng.toFixed(4)}</small>
            </div>
          `,
          offset: new AMap.Pixel(0, -30)
        })
        info.open(map.value, marker.getPosition())
      })
    })
  }

  const addMarker = async ({ lng, lat, type, description }) => {
    try {
      const { data } = await createAlert({
        threat_level: type || 'medium',
        description: description || '',
        latitude: lat,
        longitude: lng,
        source: 'manual'
      })

      const markerData = {
        id: data.id,
        lng,
        lat,
        type: type || 'medium',
        description: description || '',
        time: new Date().toISOString()
      }
      markers.value.push(markerData)

      const marker = new AMap.Marker({
        position: [lng, lat],
        title: description,
        icon: createMarkerIcon(type)
      })
      marker.setMap(map.value)

      return markerData
    } catch (e) {
      console.error('添加标记失败', e)
      return null
    }
  }

  const removeMarker = (id) => {
    markers.value = markers.value.filter(m => m.id !== id)
  }

  const clearMarkers = async () => {
    try {
      await deleteAlerts('manual')
    } catch { /* 后端删除失败时仅清空本地显示 */ }
    markers.value = []
    if (map.value) map.value.clearMap()
  }

  const exportMarkers = () => {
    const json = JSON.stringify(markers.value, null, 2)
    const blob = new Blob([json], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `markers_${new Date().toISOString().slice(0, 10)}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  // ── 创建标记图标 ──
  const createMarkerIcon = (type) => {
    const color = markerColors[type] || '#f44336'
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="32" height="44" viewBox="0 0 32 44">
      <path d="M16 0C8.28 0 2 6.28 2 14c0 10.5 14 28 14 28s14-17.5 14-28C30 6.28 23.72 0 16 0z"
        fill="${color}" stroke="#fff" stroke-width="2"/>
      <circle cx="16" cy="14" r="6" fill="#fff" opacity="0.9"/>
    </svg>`
    return new AMap.Icon({
      size: new AMap.Size(32, 44),
      imageSize: new AMap.Size(32, 44),
      image: 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg)
    })
  }

  // ── 定位 ──
  const getCurrentPosition = () => {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error('浏览器不支持定位'))
        return
      }
      navigator.geolocation.getCurrentPosition(
        (pos) => resolve({
          lat: pos.coords.latitude,
          lng: pos.coords.longitude
        }),
        (err) => {
          const messages = {
            1: '定位权限被拒绝',
            2: '无法获取位置信息',
            3: '定位超时'
          }
          reject(new Error(messages[err.code] || '定位失败'))
        },
        { enableHighAccuracy: true, timeout: 10000 }
      )
    })
  }

  const updateCurrentLocationMarker = (position) => {
    if (!map.value) return

    if (currentLocationMarker.value) {
      currentLocationMarker.value.setMap(null)
    }

    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
      <circle cx="12" cy="12" r="10" fill="#2196f3" opacity="0.3"/>
      <circle cx="12" cy="12" r="6" fill="#2196f3" opacity="0.6"/>
      <circle cx="12" cy="12" r="3" fill="#fff"/>
    </svg>`

    currentLocationMarker.value = new AMap.Marker({
      position: [position.lng, position.lat],
      icon: new AMap.Icon({
        size: new AMap.Size(30, 30),
        imageSize: new AMap.Size(30, 30),
        image: 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg)
      }),
      zIndex: 100
    })
    currentLocationMarker.value.setMap(map.value)
    map.value.setCenter([position.lng, position.lat])
  }

  const startLocationTracking = () => {
    getCurrentPosition().then(pos => {
      updateCurrentLocationMarker(pos)
      locationInterval.value = setInterval(() => {
        getCurrentPosition().then(p => updateCurrentLocationMarker(p)).catch(() => {})
      }, LOCATION_INTERVAL)
    }).catch(() => {})
  }

  const stopLocationTracking = () => {
    if (locationInterval.value) {
      clearInterval(locationInterval.value)
      locationInterval.value = null
    }
  }

  // ── 模式切换 ──
  const enableAddMode = () => { isAddingMode.value = true }
  const cancelAddMode = () => { isAddingMode.value = false }

  // ── 演示数据：骑行轨迹（南邮仙林校区周边，硬件未到货时展示） ──
  const drawDemoRoute = () => {
    if (!map.value || !window.AMap) return
    // 仙林校区周边一条示意骑行路线
    const route = [
      [118.9075, 32.1185],
      [118.9102, 32.1192],
      [118.9135, 32.1188],
      [118.9158, 32.1172],
      [118.9146, 32.1151],
      [118.9112, 32.1143],
      [118.9081, 32.1156]
    ]
    const polyline = new AMap.Polyline({
      path: route,
      strokeColor: '#22d3ee',
      strokeWeight: 4,
      strokeOpacity: 0.9,
      lineJoin: 'round',
      showDir: true
    })
    polyline.setMap(map.value)

    // 当前位置（起点，呼吸点）
    const start = new AMap.Marker({
      position: route[0],
      zIndex: 200,
      content: `<div style="width:20px;height:20px;border-radius:50%;background:#22d3ee;box-shadow:0 0 0 6px rgba(34,211,238,0.25),0 0 18px #22d3ee;"></div>`,
      offset: new AMap.Pixel(-10, -10)
    })
    start.setMap(map.value)
  }

  // ── 演示数据：假预警点 ──
  const drawDemoAlerts = () => {
    if (!map.value || !window.AMap) return
    const demos = [
      { lng: 118.9135, lat: 32.1188, type: 'high', desc: '事故高发路段（演示）' },
      { lng: 118.9158, lat: 32.1172, type: 'medium', desc: '路面障碍（演示）' },
      { lng: 118.9112, lat: 32.1143, type: 'low', desc: '缓行提醒（演示）' }
    ]
    demos.forEach((d) => {
      const m = new AMap.Marker({
        position: [d.lng, d.lat],
        title: d.desc,
        icon: createMarkerIcon(d.type)
      })
      m.setMap(map.value)
      m.on('click', () => {
        const info = new AMap.InfoWindow({
          content: `<div style="padding:10px;max-width:200px;color:#070b16"><b>${d.desc}</b><p style="margin:5px 0;font-size:12px">${d.lat.toFixed(4)}, ${d.lng.toFixed(4)}</p></div>`,
          offset: new AMap.Pixel(0, -30)
        })
        info.open(map.value, m.getPosition())
      })
    })
  }

  // ── 销毁 ──
  const destroy = () => {
    stopLocationTracking()
    if (map.value) {
      map.value.destroy()
      map.value = null
    }
  }

  return {
    map,
    geolocation,
    markers,
    currentLocationMarker,
    isAddingMode,
    markerColors,
    initMap,
    loadMarkers,
    renderMarkers,
    addMarker,
    removeMarker,
    clearMarkers,
    exportMarkers,
    getCurrentPosition,
    updateCurrentLocationMarker,
    startLocationTracking,
    stopLocationTracking,
    enableAddMode,
    cancelAddMode,
    drawDemoRoute,
    drawDemoAlerts,
    destroy
  }
}
