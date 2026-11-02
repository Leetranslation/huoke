import axios from 'axios'

const http = axios.create({
  baseURL: '',
  timeout: 120000,
})

export const campaignApi = {
  list: () => http.get('/campaigns'),
  create: (data) => http.post('/campaigns', data),
  import: (id) => http.post(`/campaigns/${id}/import`),
  crawl: (id, customerTypes, maxCompanies = 5, dataSource = 'deepseek') =>
    http.post(`/campaigns/${id}/crawl`, null, {
      params: {
        customer_types: customerTypes,
        max_companies: maxCompanies,
        data_source: dataSource,
      },
      timeout: 300000,
    }),
  profile: (id) => http.post(`/campaigns/${id}/profile`),
  analyzeDna: (id) => http.post(`/campaigns/${id}/analyze-dna`, null, { timeout: 120000 }),
  extractContacts: (id) =>
    http.post(`/campaigns/${id}/extract-contacts`, null, { timeout: 300000 }),
  companies: (id) => http.get(`/campaigns/${id}/companies`),
}

export const companyApi = {
  list: () => http.get('/companies'),
  get: (id) => http.get(`/companies/${id}`),
  translate: (id) => http.post(`/companies/${id}/translate`),
  replies: (id) => http.get(`/companies/${id}/replies`),
}

export const emailApi = {
  list: () => http.get('/emails'),
  generate: (companyId, contactId) =>
    http.post(`/companies/${companyId}/emails`, { contact_id: contactId }),
  submit: (id) => http.post(`/emails/${id}/submit`),
  approve: (id) => http.post(`/emails/${id}/approve`),
  reject: (id) => http.post(`/emails/${id}/reject`),
  send: (id) => http.post(`/emails/${id}/send`),
  update: (id, data) => http.patch(`/emails/${id}`, data),
  event: (id, eventType) => http.post(`/emails/${id}/events`, { event_type: eventType }),
}

export const contactApi = {
  list: () => http.get('/contacts'),
  runFollowup: () => http.post('/followup/run'),
  checkReplies: () => http.post('/followup/check-replies'),
  lastScan: () => http.get('/followup/last-scan'),
}

export default http
