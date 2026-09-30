import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getCourseAnalyticsDashboard } from '../services/api'
import '../App.css'
import './AnalyticsDashboard.css'


function AnalyticsDashboard() {
  const [analytics, setAnalytics] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const testCourseId = 3


  useEffect(() => {
    async function loadAnalytics() {
      try {
        setLoading(true)
        setError('')

        const data = await getCourseAnalyticsDashboard(
          testCourseId,
        )

        setAnalytics(data)
      } catch (err) {
        setError(
          err.message || 'تعذر تحميل مؤشرات الدورة',
        )
      } finally {
        setLoading(false)
      }
    }

    loadAnalytics()
  }, [])


  const registeredTrainees =
    analytics?.registration?.registered_trainees ?? 0

  const attendanceRate =
    analytics?.attendance?.attendance_rate ?? 0

  const absenceRate =
    analytics?.attendance?.absence_rate ?? 0

  const evaluationAverage =
    analytics?.evaluation?.average ?? 0

  const evaluationResponseRate =
    analytics?.evaluation?.response_rate ?? 0

  const impactScore =
    analytics?.impact?.score ?? 0

  const impactResponseRate =
    analytics?.impact?.response_rate ?? 0

  const completionRate =
    analytics?.content?.completion_rate ?? 0

  const occupancyRate =
    analytics?.capacity?.occupancy_rate ?? 0

  const courseName =
    analytics?.course_name || 'الدورة التجريبية للتحليلات'


  return (
    <div className="dashboard-page" dir="rtl">

      <aside className="dashboard-sidebar">

        <div className="sidebar-brand">
          <h1>أثر</h1>
          <span>من التعلم إلى التغيير.</span>
        </div>

        <div className="sidebar-label">
          مساحة الإدارة
        </div>

        <nav className="sidebar-nav">

          <Link
            to="/admin"
            className="nav-item"
          >
            <span className="nav-icon">⌂</span>
            <span>الرئيسية</span>
          </Link>

          <Link
            to="/programs"
            className="nav-item"
          >
            <span className="nav-icon">▤</span>
            <span>الدورات التدريبية</span>
          </Link>

          <Link
            to="/admin/analytics"
            className="nav-item active"
          >
            <span className="nav-icon">▥</span>
            <span>التقارير والمؤشرات</span>
          </Link>

        </nav>

      </aside>


      <main className="dashboard-main">

        <header className="dashboard-header">

          <div>
            <p className="dashboard-eyebrow">
              التحليلات والتقارير
            </p>

            <h2>
              لوحة المؤشرات والتقارير
            </h2>

            <p className="dashboard-subtitle">
              متابعة بيانات التسجيل والحضور والتقييم
              وقياس أثر التدريب.
            </p>
          </div>

        </header>


        {loading && (
          <section className="analytics-course-section">
            <div className="analytics-course-header">
              جاري تحميل مؤشرات الدورة...
            </div>
          </section>
        )}


        {error && (
          <section className="analytics-course-section">
            <div className="analytics-course-header">
              {error}
            </div>
          </section>
        )}


        {!loading && !error && (
          <>
            <section className="analytics-course-section">

              <div className="analytics-course-header">

                <div>
                  <span className="analytics-label">
                    الدورة التدريبية
                  </span>

                  <h3>
                    {courseName}
                  </h3>
                </div>

                <select
                  className="analytics-course-select"
                  value={testCourseId}
                  disabled
                  readOnly
                >
                  <option value={testCourseId}>
                    {courseName}
                  </option>
                </select>

              </div>

            </section>


            <section className="analytics-kpi-grid">

              <div className="analytics-kpi-card">
                <span className="analytics-kpi-title">
                  عدد المسجلين
                </span>

                <strong className="analytics-kpi-value">
                  {registeredTrainees}
                </strong>

                <span className="analytics-kpi-note">
                  متدرب
                </span>
              </div>


              <div className="analytics-kpi-card">
                <span className="analytics-kpi-title">
                  نسبة الحضور
                </span>

                <strong className="analytics-kpi-value">
                  {attendanceRate}%
                </strong>

                <span className="analytics-kpi-note">
                  من إجمالي الحضور
                </span>
              </div>


              <div className="analytics-kpi-card">
                <span className="analytics-kpi-title">
                  متوسط التقييم
                </span>

                <strong className="analytics-kpi-value">
                  {evaluationAverage}
                </strong>

                <span className="analytics-kpi-note">
                  من 5
                </span>
              </div>


              <div className="analytics-kpi-card">
                <span className="analytics-kpi-title">
                  مؤشر الأثر
                </span>

                <strong className="analytics-kpi-value">
                  {impactScore}
                </strong>

                <span className="analytics-kpi-note">
                  من 5
                </span>
              </div>

            </section>


            <section className="analytics-details-grid">

              <div className="analytics-card">

                <div className="analytics-card-header">
                  <div>
                    <span className="analytics-label">
                      الحضور
                    </span>

                    <h3>
                      الحضور والغياب
                    </h3>
                  </div>
                </div>

                <div className="analytics-empty-chart">
                  <strong>
                    {attendanceRate}%
                  </strong>

                  <span>
                    نسبة الحضور
                  </span>
                </div>

                <div className="analytics-stat-row">

                  <div>
                    <span>الحضور</span>
                    <strong>
                      {attendanceRate}%
                    </strong>
                  </div>

                  <div>
                    <span>الغياب</span>
                    <strong>
                      {absenceRate}%
                    </strong>
                  </div>

                </div>

              </div>


              <div className="analytics-card">

                <div className="analytics-card-header">
                  <div>
                    <span className="analytics-label">
                      الطاقة الاستيعابية
                    </span>

                    <h3>
                      إشغال المقاعد
                    </h3>
                  </div>
                </div>

                <div className="analytics-progress-block">

                  <div className="analytics-progress-info">
                    <span>
                      نسبة الإشغال
                    </span>

                    <strong>
                      {occupancyRate === null
                        ? 'غير محدد'
                        : `${occupancyRate}%`}
                    </strong>
                  </div>

                  <div className="analytics-progress">
                    <div
                      className="analytics-progress-value"
                      style={{
                        width:
                          occupancyRate === null
                            ? '0%'
                            : `${Math.min(
                                occupancyRate,
                                100,
                              )}%`,
                      }}
                    />
                  </div>

                </div>

                <p className="analytics-card-note">
                  نسبة المقاعد المشغولة من الطاقة
                  الاستيعابية للدورة.
                </p>

              </div>


              <div className="analytics-card">

                <div className="analytics-card-header">
                  <div>
                    <span className="analytics-label">
                      المحتوى التدريبي
                    </span>

                    <h3>
                      إكمال المحتوى
                    </h3>
                  </div>
                </div>

                <div className="analytics-progress-block">

                  <div className="analytics-progress-info">
                    <span>
                      نسبة الإكمال
                    </span>

                    <strong>
                      {completionRate}%
                    </strong>
                  </div>

                  <div className="analytics-progress">
                    <div
                      className="analytics-progress-value"
                      style={{
                        width: `${Math.min(
                          completionRate,
                          100,
                        )}%`,
                      }}
                    />
                  </div>

                </div>

                <p className="analytics-card-note">
                  نسبة المتدربين الذين أكملوا
                  المحتوى المطلوب.
                </p>

              </div>

            </section>


            <section className="analytics-bottom-grid">

              <div className="analytics-card">

                <div className="analytics-card-header">
                  <div>
                    <span className="analytics-label">
                      تقييم الدورة
                    </span>

                    <h3>
                      رضا المتدربين
                    </h3>
                  </div>
                </div>

                <div className="analytics-score">

                  <strong>
                    {evaluationAverage}
                  </strong>

                  <span>
                    متوسط التقييم من 5
                  </span>

                </div>

                <div className="analytics-response-rate">
                  <span>
                    نسبة الاستجابة
                  </span>

                  <strong>
                    {evaluationResponseRate}%
                  </strong>
                </div>

              </div>


              <div className="analytics-card">

                <div className="analytics-card-header">
                  <div>
                    <span className="analytics-label">
                      قياس الأثر
                    </span>

                    <h3>
                      أثر التدريب
                    </h3>
                  </div>
                </div>

                <div className="analytics-score">

                  <strong>
                    {impactScore}
                  </strong>

                  <span>
                    مؤشر الأثر من 5
                  </span>

                </div>

                <div className="analytics-response-rate">
                  <span>
                    نسبة الاستجابة
                  </span>

                  <strong>
                    {impactResponseRate}%
                  </strong>
                </div>

              </div>

            </section>
          </>
        )}

      </main>

    </div>
  )
}


export default AnalyticsDashboard